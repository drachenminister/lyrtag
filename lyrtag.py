#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Embed song lyrics in id3-tags (c) 2015 by drachenminister

This script traverses the given path, tries to find its lyrics online
and embeds it in a USLT frame in the files id3-tag.

It uses the my own lyrscraper module for the online lookup and
mutagen.id3 for the tagging.

Example usage::
        lyrtag /media/data/MyMusic

"""
import os
import sys

import lyrscraper
from mutagen.id3 import ID3, USLT, ID3NoHeaderError


def main():
    """Traverse path and embed lyrics. Log work to logfile.

    Args:
        sys.argv[1] (string): path to traverse

    """
    for root, dirs, files in os.walk(sys.argv[1]):
        for file in files:
            if file.endswith(".mp3"):
                file=(os.path.join(root, file))

                # get tag from file
                tag = get_tag(file)
                if not tag:
                    error('no id3tag: ' + file)
                    continue

                # skip if frame exists
                if has_USLT(tag):
                    log('existing USLT tag: ' + file)
                    continue

                # get lyric
                lyric = lyrscraper.lyric(tag)
                if not lyric:
                    log('no lyric: ' + file)
                    continue

                # save lyric frame
                tag[u"USLT::"] = (USLT(encoding=3, lang=u'eng',
                                       desc=u'lyrics.wikia.com', text=lyric))
                tag.save(file)
                log('lyrics written: ' + file)


def log( message ):
    """Logs a message to the logfile.

    Args:
        message (string): Message to write to logfile

    """
    with open("lyrtag.log", "a") as log:
        log.write(message + '\n')
        log.close
    return


def error( message ):
    """Logs an error message to the logfile.

    Args:
        message (string): Message to write to logfile

    """
    message = 'ERROR: ' + message
    log (message)
    return


def get_tag( file ):
    """Get the id3-tag from a given file.

    Args:
        file (string): full file path

    Returns:
        ID3: id3-tag if successful, None otherwise

    """
    try:
        tag = ID3(file)
    except ID3NoHeaderError:
        error('no ID3 header: ' + file)
        return None
    return tag


def has_USLT( tag ):
    """Checks if the given tag already has an apropriate frame.

    Args:
        tag (ID3): id3-tag to check

    Returns:
        bool: True if frame is already there, False otherwise

    """
    if len(tag.getall(u"USLT:lyrics.wikia.com:'eng'")) != 0:
        return True
    else:
        return False

if __name__ == '__main__':
    main()
