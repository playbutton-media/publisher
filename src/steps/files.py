import datetime
import logging
import os

import eyed3

from src import shared, ui
from src.internalconf import COVER_ART_FORMATS


class Renamer:
    def __init__(self, config, data):
        self.data = data
        self.config = config
        self.schemes = shared.Schemer(config, data)
        self.utils = shared.Utils(config)

    def map(self):
        """
        renames audios, videos, covers, descriptions, project files
        :return:
        """
        ret = dict()
        newtracksdata = self.data.get('tracks')
        for i, track in enumerate(self.data.get('tracks')):
            # rename audios
            src = track.get('filename')
            dst = self.schemes.get('paths/renamed/audios',
                                   tracknum=track['tracknum'],
                                   track_title=track['track_title'],
                                   artist=track['artist'],
                                   )
            if src != dst and os.path.isfile(src):
                ret[src] = dst
            newtracksdata[i]['filename'] = dst
            # rename videos
            src = track.get('video')
            dst = self.schemes.get('paths/renamed/videos',
                                   tracknum=track['tracknum'],
                                   track_title=track['track_title'],
                                   artist=track['artist'],
                                   )
            if src != dst and os.path.isfile(src):
                ret[src] = dst
            newtracksdata[i]['video'] = dst

        # rename cover arts
        for format in COVER_ART_FORMATS:
            for resolution in ('low_res', 'full_res'):
                schemename = f'covers{"-lowres" if resolution == "low_res" else ""}'

                src = self.schemes.get(f'paths/files/{schemename}', format=format)
                dst = self.schemes.get(f'paths/renamed/{schemename}', format=format)

                if src != dst and os.path.isfile(src):
                    ret[src] = dst

        # rename descriptions
        for lang in self.config.get('description-languages'):
            src = self.schemes.get('paths/files/descriptions', lang=lang)
            dst = self.schemes.get('paths/renamed/descriptions', lang=lang)

            if src != dst and os.path.isfile(src):
                ret[src] = dst

        # rename project files
        pjfiles_dir = os.path.dirname(self.schemes.get('paths/files/project-files', filename='_'))
        for pjfile in self.utils.listdir(pjfiles_dir):
            src = self.schemes.get('paths/files/project-files', filename=pjfile)
            dst = self.schemes.get('paths/renamed/project-files', filename=pjfile)

            if src != dst and os.path.isfile(src):
                ret[src] = dst

        return ret, newtracksdata

    def rename(self):
        rename_map, newtracksdata = self.map()

        for src, dst in rename_map.items():
            logging.debug(f"MV {src} --> {dst}")
            os.rename(src, dst)
            self.data['tracks'] = newtracksdata


def rename(config, data, reverse=False):
    renamer = Renamer(data=data, config=config)
    rename_map, _ = renamer.map()
    if reverse:
        rename_map = {v:k for k,v in rename_map.items()}
    if len(rename_map) < 1:
        logging.debug(f"Found no files to rename. (all tracks filename match dirs/renamed/audios)")
        return True

    if config.get('options/confirm/rename-tracks'):
        if config.get('options/contract-rename-map'):
            rename_map_disp = dict()
            for k, v in rename_map.items():
                commonprefix = os.path.commonprefix((k, v))
                k = '(...)' + os.path.sep + k.replace(commonprefix, '', 1)
                v = '(...)' + os.path.sep + v.replace(commonprefix, '', 1)
                rename_map_disp[k] = v
        else:
            rename_map_disp = rename_map

        print(ui.pprint_dict(rename_map_disp, sep='--> '))
        if not ui.ask('Rename ?', choices='yn', default='y'):
            return False

    renamer.rename()
    return True


class Metadata:
    def __init__(self, config, data):
        self.config = config
        self.data = data
        self.schemes = shared.Schemer(config, data)

    def preview(self):
        # get date components for eyed3's custom Date() class
        date_y = int(datetime.date.today().strftime('%Y'))
        date_m = int(datetime.date.today().strftime('%m'))
        date_d = int(datetime.date.today().strftime('%d'))
        # get total count of tracks
        tracklist = self.data.get('tracks')
        total = len(tracklist)

        metadata = {
            "Artist"      : self.data.get('artist'),
            "Album"       : self.data.get('title'),
            "Cover art"   : self.schemes.get('paths/renamed/covers', format='square'),
            "Date"        : f'{date_d}/{date_m}/{date_y}',
            "Title"       : ui.colored('track\'s title', color='red'),
            "Track number": ui.colored(f'1-{total}', color='red') + f'/{total}'
        }

        return metadata

    def apply(self, metadata=None):
        if not metadata:
            metadata = self.preview()

        date_y = int(datetime.date.today().strftime('%Y'))
        date_m = int(datetime.date.today().strftime('%m'))
        date_d = int(datetime.date.today().strftime('%d'))
        applied_count = 0
        for track in self.data.get('tracks'):

            filename = self.schemes.get('paths/renamed/audios', **track)

            logging.debug(f'Loading "{os.path.split(filename)[0]}" into eyed3...')
            audiofile = eyed3.load(filename)

            # artist
            audiofile.tag.artist = audiofile.tag.album_artist = metadata['Artist']
            # title
            audiofile.tag.title = track['track_title']
            # album title
            audiofile.tag.album = metadata['Album']
            # track number (current, total)
            audiofile.tag.track_num = (track['tracknum'], len(self.data.get('tracks')))
            # release date YYYY-MM-dd
            audiofile.tag.original_release_date = eyed3.core.Date(year=date_y, day=date_d, month=date_m)
            audiofile.tag.release_date = eyed3.core.Date(year=date_y, day=date_d, month=date_m)
            # album arts (type, imagedata, imagetype, description)
            audiofile.tag.images.set = (
                3, metadata['Cover art'], 'image/png', self.config.get('defaults/covers-description'))

            logging.debug(f'Saving tags into {filename}...')
            try:
                audiofile.tag.save()
                applied_count += 1
            except Exception as e:
                logging.error('eyed3 error:' + str(e))

        logging.info(f'Applied metadata to {applied_count} audio file{"s" if applied_count != 1 else ""}')


def metadata(config, data):
    metadatator = Metadata(config, data)
    if config.get('options/confirm/apply-metadata'):
        preview = metadatator.preview()
        logging.info("The following metadata will be applied:")
        ui.pprint_dict(preview)
        if not ui.ask('Apply ?', choices='yn', default='y'):
            return False

    metadatator.apply()