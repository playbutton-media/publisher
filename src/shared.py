import logging
import os
import re
import sys
import webbrowser


class Schemer:
    def __init__(self, config, data):
        self.config = config
        self.data = data
        self.placeholder = re.compile('<([\w_]+)>')
        self.config_placeholder = re.compile('<<(.+)>>')

    def _to_regex(self, scheme):
        scheme = scheme.replace('\\', '/')
        # scheme = self.config.get(scheme)
        for placeholder in self.placeholder.findall(scheme):
            # todo support for type declarators (\d+ or \w+ instead of .+)
            scheme = scheme.replace(f'<{placeholder}>', f'(?P<{placeholder}>.+)')
        logging.debug(f'regexed: -> {scheme}')

        return re.compile(scheme)

    def _unknown_placeholders(self, scheme, data):
        for placeholder in self.placeholder.findall(scheme):
            if placeholder not in data.keys():
                logging.error(f'Placeholder <{placeholder}> unavailable for scheme {scheme}')

    def extract(self, scheme, string):
        if scheme.startswith('paths'):
            string = string.replace('\\','/')
        scheme_req = scheme
        scheme_ = self.config.get(scheme)
        # backslashes are not regex's friends, constantly getting errors. Might need to convert
        # it back.
        scheme = self._to_regex(scheme_)

        if not scheme.match(string):
            raise ValueError(f"Trying to extract info but pattern does not match string (scheme={scheme_};string={string})")
            return [[]]

        extracted = [e.groupdict() for e in scheme.finditer(string)]
        if len(extracted) < 1:
            logging.error(f"Couldn't extract any info (scheme={scheme};string={string})")
            return [[]]
        else:
            return extracted

    def match(self, scheme, string):
        return self.get(scheme) == string

    def scheme_match(self, scheme, string):
        if scheme.startswith('paths'):
            string = string.replace('\\','/')
        regex = self.config.get(scheme)
        regex = self._to_regex(regex)
        ret = regex.match(string)

        logging.debug(f'matching {regex} against {string}: {ret}')

        return ret


    def apply(self, scheme, **data):
        loaded_scheme = self.config.get(scheme)
        self._unknown_placeholders(scheme, data)
        processed = loaded_scheme
        for placeholder in self.placeholder.findall(loaded_scheme):
            processed = processed.replace(f'<{placeholder}>', str(data[placeholder]))

        for placeholder in self.config_placeholder.findall(loaded_scheme):
            processed = processed.replace(f'<<{placeholder}>>', self.config.get(placeholder))

        if scheme.startswith('paths'):
            processed = os.path.realpath(os.path.expanduser(processed))

        return processed

    def get(self, scheme, **additional_data):
        data = {**self.data, **additional_data}
        return self.apply(scheme, **data)


class Utils:
    def __init__(self, config):
        self.config = config

    def listdir(self, dir, empty_fatal=True):

        def handle_err(msg, level=logging.FATAL, mkdir=True):
            # warns the user
            logging.log(level, f'The directory "{dir}" ' + msg)
            # create directory
            if self.config.get('options/automatic/create-dirs') and mkdir:
                logging.info(f'Creating directory ...')
                os.makedirs(dir, exist_ok=True)
                if self.config.get('options/automatic/open-dirs'):
                    # open directory
                    logging.info(f'Opening directory...')
                    webbrowser.open(dir)

            if self.config.get('options/automatic/open-dirs') and not mkdir:
                # open directory
                logging.info(f'Opening directory...')
                webbrowser.open(dir)
            # exit program if loglevel is fatal
            if level == logging.FATAL:
                sys.exit()

        if not os.path.isdir(dir):
            handle_err("doesn't exist")
        elif len(os.listdir(dir)) < 1:
            loglevel = logging.FATAL if empty_fatal else logging.WARNING
            handle_err("is empty", level=loglevel, mkdir=False)
        else:
            return os.listdir(dir)


def slugify(data, sub='-'):
    ret = re.sub(r'[^\w-]', sub, data).lower()
    # remove consecutive duplicates of "sub"
    ret = re.sub(str(sub)+r'{2,}',sub, ret)
    # remove trailing & leading subs
    ret = ret.strip('-')
    return ret


def plural(string, number, suffix='s'):
    if number == 1:
        return string
    else:
        return string+suffix

