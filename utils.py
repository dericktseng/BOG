from constants import SC2EXT
import pathlib
from discord.message import Attachment


def is_replay(attachment: Attachment) -> bool:
    """ determines whether given attachment is an SC2Replay. """
    file_ext = pathlib.Path(attachment.filename).suffix
    return file_ext == SC2EXT and attachment.content_type == None


def boLine(buildOrderLine: dict) -> str:
    """ return string in format '00:24 Zealot' if not worker """
    if buildOrderLine['is_worker']:
        return ''
    return buildOrderLine['time'] + ' ' + buildOrderLine['name']



def pad(string: str, length: int) -> str:
    """ pads string with spaces at end so that it will use length characters """
    diff = length - len(string)
    if diff > 0:
        return string + ' ' * diff
    else:
        return string


def arr_to_string(arr: list, cutoff: float) -> str:
    """ Converts arr to string table, with cutoff length of characters
    arr is given as an array of arrays of strings, all of arbitrary length.
    expects every string in its list to have the same length
    e.g. arr
    [
        ['line 1', 'line 2'],
        ['line 12', 'line 23', 'line 34']
    ]

    returns:
        line 1 | line 12
        line 2 | line 23
               | line 34
    """
    # removes empty columns from arr
    lst = [col for col in arr if col]
    max_lines = max([len(col) for col in lst])
    paddings = [len(col[0]) for col in lst]

    totalLen = 0
    result = ''
    
    for i in range(max_lines):
        nextstr = ''

        for col in range(len(lst)):
            if col != 0:
                nextstr += ' | '

            if i >= len(lst[col]):
                nextstr += ' ' * paddings[col]
            else:
                nextstr += lst[col][i]

        totalLen += len(nextstr) + 1 # +1 accounts for newline character
        if totalLen < cutoff:
            result += nextstr + "\n"
        else:
            break
            
    return result.strip()


def get_replay_strs(replaydata: dict) -> str:
    """ Obtains the formatted build order string from replaydata.
    ReplayData is the data obtained from spawningtool parser as documented
    https://github.com/StoicLoofah/spawningtool/wiki/Diving-into-the-Data
    """
    mapname = replaydata['map']
    players = replaydata['players']
    game_type = replaydata['game_type']
    globaldata = game_type + ' ' + mapname

    stringarray = list()

    for p in players:
        player = players[p]
        if not player['is_human']:
            continue
        strlist = list()

        name = player['name']
        result = player['result']
        race = player['pick_race']
        header = f'{name} ({race}): {result}'
        headerlen = len(header)

        bo = player['buildOrder']
        longestLineLen = max([len(boLine(l)) for l in bo])
        maxlen = max(headerlen, longestLineLen)

        linebreak = '-' * maxlen

        strlist.append(pad(header, maxlen))
        strlist.append(linebreak)

        # obtains all elements that are not workers
        for elem in filter(lambda e: not e['is_worker'], bo):
            strlist.append(pad(boLine(elem), maxlen))

        stringarray.append(strlist)

    totalstr = arr_to_string(stringarray, float('inf'))
    return f'{globaldata}\n{totalstr}'
