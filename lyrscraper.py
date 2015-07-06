#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Lyrscraper (c) 2015 by drachenminister

This module provides functions to scrape song lyrics off of
lyrics.wikia.com only but it can easyly be adopted to work with other
sites aswell.

How it works:
    The API of lyrics.wikia.com only provides a smal section of the
    lyrics alongside with an URL of a web page that displays the
    complete lyrices.
    Therefor to get the lyrics we first call the API for that URL and
    then scrape the apropriate section of the resulting page.

How it can be adapted to use other sities:
    Asuming the same two step aproach is needed: For step 1 you would
    have to change the APIs URL, parameters and untangling.
    For step 2 you would have to check string replacements and xpath
    definition.

"""
import urllib

import untangle
import requests
from lxml import html


def _url(id3tag):
    """Get the lyric's URL by calling the API

    Extract song and artist frames from the id3tag and then call
    the lyrics.wikia.com api for the URL of the actual lyric.

    Args:
        id3tag (ID3): id3-tag of the song

    Returns:
        string: lyric URL if successful, None otherwise

    """
    try:
        # Get artist and song from tag
        artist = id3tag['TPE1'].text[0].encode('utf8')
        song = id3tag['TIT2'].text[0].encode('utf8')

        # Build request
        params = {'artist':artist, 'song':song, 'fmt':'xml'}
        request = 'http://lyrics.wikia.com/api.php?' + urllib.urlencode(params)

        # Do request
        response = untangle.parse(request)
        if response.LyricsResult.lyrics.cdata == 'Not found':
            return None
        return urllib.unquote(response.LyricsResult.url.cdata)

    except Exception:
        return None


def scrape(url):
    """Open the URL and scrape the lyric.

    Opens the URL and scrapes the lyric off the apropriate
    div stripping anything else but text carefully keeping
    blank lines though.

    Args:
        url (string): URL to scrape

    Returns:
        string: Lyric if successful, None otherwise

    """
    try:
        # Get page
        page = requests.get(url)
        page.raise_for_status()

        # Scrape page
        tree = html.fromstring(page.text.replace('<br />', '\n'))
        return tree.xpath('//div[@class="lyricbox"]/text()')[0]

    except Exception:
        return None


def lyric(id3tag):
    """Return the lyric to a song

    Takes an id3 tag and returns the lyric of the correspondig
    song as a unicode string

    Args:
        id3tag (ID3): id3-tag of the song

    Returns:
        string: Lyric if successful, None otherwise

    """
    # Get lyric url
    lyrurl = _url(id3tag)
    if not lyrurl:
        return None

    # Scrape url
    return scrape(lyrurl)


if __name__ == '__main__':
    """Print lyric to standard out

    Takes a filename from commandline extracts the id3-tag and prints
    the lyric according to song and artist frames to standard out.

    Args:
        sys.argv[1] (string): Filename

    """
    import sys
    from mutagen.id3 import ID3

    try:
        tag = ID3(sys.argv[1])
        print lyric(tag)
    except Execption:
        pass
