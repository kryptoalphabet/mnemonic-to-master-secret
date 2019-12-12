"""
Python 3

Convert a BIP39 mnemonic phrase to the master secret.
For example convert a 12 or 24 word mnemonic phrase like:

jaguar brief plastic chaos bundle crew safe vanish guess arm damp charge
dwarf short exclude vocal spirit middle expose must tissue ten scout unaware

into it's master secret where the mnemonic phrase is actually derived from:

77237E981321E466AF878A676174DC93444BFAAD2118942C90E2DBDF057

This can be verified with the following command from the libbitcoin explorer:

bx mnemonic-new 77237E981321E466AF878A676174DC93444BFAAD2118942C90E2DBDF057

which return the nmemonic. This is all needed for TREZORs' shamir secret
sharing tool. They need the master secret instead of the mnemonic phrase.
German video to do this can be found on YouTube at 'Krypto Alphabet' channel.

IMPORTANT:
If you're using a live system like Tails you have to manually download the
BIP39 wordlist from github as the download from the script will fail:

https://raw.githubusercontent.com/bitcoin/bips/master/bip-0039/english.txt
"""


import sys
from os import path
from time import sleep
from urllib.request import urlopen
from urllib.error import URLError, HTTPError


# Url to the 2048 BIP39 words used by the mnemonic phrase
URL_WORDLIST = "https://raw.githubusercontent.com/bitcoin/bips/master/bip-0039/{}.txt"
# You might want to adjust to a different language: chinese_simplified, 
# chinese_traditional, czech, french, italian, japanese, korean, spanish
LANGUAGE = "english"


def check_wordlist():
	"""Verify the text file with the words exists otherwise download it."""
	if not path.exists("{}.txt".format(LANGUAGE)):
		attempts = 0
		while attempts < 3:
			try:
				resp = urlopen(URL_WORDLIST.formt(LANGUAGE))
				data = resp.read()
				f = open("{}.txt".format(LANGUAGE), "w")
				f.write(data)
				f.close()
			except URLError as e:
				attempts += 1
				print(e.reason)
				sleep(3)
			except HTTPError as e:
				attempts += 1
				print(e.reason)
				sleep(3)


def get_indexes(args):
    """Get all indexes (as number) from the words list."""
    check_wordlist()

    numbers = []
    for word in args:
        with open("{}.txt".format(LANGUAGE)) as wordlist:
            for index, line in enumerate(wordlist):
                if word == line.rstrip():
                    numbers.append(index)
    return numbers


def convert_to_binary(numbers):
	"""Convert the numbers to a long string of binary digits."""
    binary = ""
    for number in numbers:
        _bin = str(bin(number))[2:]  # binaries start ith 0b - remove that
        if len(_bin) < 11:
            # append zeros until binary is 11 digits long
            _bin = "0" * (11 - len(_bin)) + _bin
        binary += _bin
    return binary


def binary_to_hex(binary, words):
	"""Convert the binary string into a hex and cut first and last 2 digit."""
    seed = str(hex(int(binary, 2)))[2:]
    if words == 12:
    	# for 12 words (128 bit) only remove the last digit
    	seed = seed[:-1]
	elif words == 24:
		# for 24 words (256 bit) remove the last two digits
		seed = seed[:-2]
    return seed


# retrieve passed arguments
args = sys.argv
args.pop(0)  # remove the filename from the list

# verify if the arguments are valid - or at least the amount is correct
if len(args) != 12 and len(args) != 24:
    # this is only a very simple and bad validation
    print("ERROR - Wrong amount of words. Only tested with 12 and 24 words!")
else:
    numbers = get_indexes(args)
    # verify all passed words were in the wordslist (typo / no BIP39)
    if len(numbers) == 12 or len(numbers) == 24:
	    binary = convert_to_binary(numbers)
	    seed = binary_to_hex(binary, len(numbers))
	    print("Success!\n\n{0}\n\nverify with command:\n\nbx mnemonic-new {0}\n".format(seed))
    else:
    	print("ERROR - Please check for typo. If there is none you don\'t use BIP39 compatible words.")
