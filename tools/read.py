#!/usr/bin/env python
# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2014, Numenta, Inc.  Unless you have purchased from
# Numenta, Inc. a separate commercial license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------

from optparse import OptionParser

from fluent.model import Model
from fluent.term import Term


def readFile(filename, model, resetSequences=False, format=None):
  if model.canCheckpoint() and model.hasCheckpoint():
    model.load()

  exclusions = ('!', '.', ':', ',', '"', '\'', '\n')

  if format == "csv":
    fmt = "%s,%s,%s,%s,%s,%s,%s"
  else:
    # No format specified, so pretty print it
    fmt = "%10s | %10s | %20s | %20s | %20s | %20s | %20s"

    print(fmt %
          ("Sequence #", "Term #", "Current Term",
           "Predicted Term 1", "Predicted Term 2", "Predicted Term 3", "Predicted Term 3"))
    print("-----------------------------------"
          "-----------------------------------"
          "-----------------------------------"
          "-----------------------------------")

  s = 1
  t = 1

  with open(filename) as f:
    for line in f:
      line = "".join([c for c in line if c not in exclusions])
      strings = line.split(" ")

      for string in strings:
        if not len(string):
          continue

        term = Term().createFromString(string)
        prediction = model.feedTerm(term)
        closestStrings = prediction.closestStrings()
        closestStringsIter = iter(closestStrings)

        print(fmt %
              (s, t, string,
               next(closestStringsIter, ""),
               next(closestStringsIter, ""),
               next(closestStringsIter, ""),
               next(closestStringsIter, "")))

        t += 1

      if model.canCheckpoint():
        model.save()

      if resetSequences:
        model.resetSequence()

      s += 1
      t = 1

if __name__ == '__main__':
  parser = OptionParser("%prog file [options]")
  parser.add_option(
      "--checkpoint",
      dest="checkpoint",
      help="Directory to save model to and load model from")
  parser.add_option(
      "-f",
      "--format",
      dest="format",
      help="Format to output (ie: csv)",
      metavar="FORMAT")
  parser.add_option(
      "-r",
      "--reset-sequences",
      dest="resetSequences",
      action="store_true",
      default=False,
      help="Reset the model sequence after every line")

  (options, args) = parser.parse_args()

  if not len(args):
    parser.print_help()
    print
    raise(Exception("file required"))

  model = Model(checkpointDir=options.checkpoint)

  try:
    readFile(args[0], model,
             resetSequences=options.resetSequences, format=options.format)
  except KeyboardInterrupt:
    if model.canCheckpoint():
      print("Saving model before exiting...")
      model.save()
