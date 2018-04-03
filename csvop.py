#!/usr/bin/env python
"""
A script for performing high-level CSV file operations.
"""
__author__ = "Michael Brooks"
__copyright__ = "Copyright 2013, Michael Brooks"
__license__ = "MIT"

__all__ = ["addcolumn", "dropcolumn", "merge", "select"]

import csv
import os
import itertools

def read_csv(filename):
    with open(filename, 'rbU') as infile:
        reader = csv.reader(infile)
        data = []
        for row in reader:
            data.append(row)
        return data

def make_csv(filename, values):
    with open(filename, 'wb') as outfile:
        writer = csv.writer(outfile)
        for row in values:
            writer.writerow(row)
        
def csv_header(filename):
    with open(filename, 'rbU') as infile:
        reader = csv.reader(infile)
        header = reader.next()
        return header

def count_rows(filename):
    with open(filename, 'rbU') as infile:
        reader = csv.reader(infile)
        
        count = 0
        for row in reader:
            count += 1
            
        return count

def _convert_numbers(row):
    """Convert any numeric members of the array to be numbers.
    
    >>> _convert_numbers(['a', 'b', 'c'])
    ['a', 'b', 'c']
    >>> _convert_numbers(['a', 'b', '4'])
    ['a', 'b', 4]
    >>> _convert_numbers(['a', 'b', '-2.4'])
    ['a', 'b', -2.4]
    """
    for i in range(len(row)):
        v = row[i]
        try:
            v = int(v)
            row[i] = v
        except ValueError:
            try:
                v = float(v)
                row[i] = v
            except ValueError:
                pass
    return row
        
def col_reference(header, name=None, index=None):
    """Get the index of a column given a name or index
    
    >>> col_reference(['a', 'b', 'c'], None, 2)
    (None, 2)
    >>> col_reference(['a', 'b', 'c'], 'a', None)
    ('a', 0)
    >>> col_reference(['a', 'b', 'c'], 'b', 2)
    ('b', 1)
    """
    if name is not None:            
        index = header.index(name)
    else:
        index = index
        
    return name, index

def map_list(val_list):
    """Create a dictionary from list values to list indices.
    
    >>> m = map_list(['a', 'b', 'c'])
    >>> m['a']
    0
    >>> m['b']
    1
    >>> m['c']
    2
    >>> len(m)
    3
    """
    result = dict()
    for i, col in enumerate(val_list):
        result[col] = i
    return result

_override_confirm = True
def always_confirm(val):
    global _override_confirm
    _override_confirm = val
    
## http://code.activestate.com/recipes/541096-prompt-the-user-for-confirmation/
def confirm(prompt=None, resp=False):
    """prompts for yes or no response from the user. Returns True for yes and
    False for no.

    'resp' should be set to the default value assumed by the caller when
    user simply types ENTER.
    """
    
    if _override_confirm:
        return True
    
    if prompt is None:
        prompt = 'Confirm'

    if resp:
        prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')
        
    while True:
        ans = raw_input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print 'please enter y or n.'
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False
    
def write_csv(iterator, filename, header=None, generator=None):
    """Go through each row of the iterator writing to the given filename.
    
    If header is supplied, it is inserted prior to processing the rows.
    
    If a generator is supplied, it is used to process each row before output.
    """
    if os.path.isfile(filename):
        if not confirm("Overwrite %s?" %(filename)):
            return

    rowsWritten = 0
    colCount = 0
    with open(filename, 'wb') as outfile:
        writer = csv.writer(outfile)
        
        if header is not None:
            if generator is not None:
                header = generator(rowsWritten, header)

            colCount = len(header)
            writer.writerow(header)
            rowsWritten += 1
        
        for row in iterator:
            if generator is not None:
                row = generator(rowsWritten, row)
            
            if not colCount:
                colCount = len(row)
                
            writer.writerow(row)
            rowsWritten += 1
            
    print 'Wrote %d rows and %d columns to %s' %(rowsWritten, colCount, filename)

    
def _addcolumn_process(args):

    if args.calc is not None:
        args.calc = eval('lambda row: %s' % (args.calc))
        
    return addcolumn(args.input, args.output, args.index, args.name, args.default, args.calc)

def _addcolumn_args(parser):
    parser.add_argument('input', metavar="INPUT_CSV", help='A csv file to read from')
    parser.add_argument('output', metavar="OUTPUT_CSV", help='A csv file to write to')
    parser.add_argument('--index', '-i', type=int, help='The index to insert the column (last by default)', required=False)
    parser.add_argument('--name', '-n', help='The name of the column to add (none by default)', required=False)
    parser.add_argument('--default', '-d', help='The default cell value', required=False)
    parser.add_argument('--calc', '-c', help='The body of a lambda expression that can calculate values based on the current row')
    parser.set_defaults(func=_addcolumn_process)

def addcolumn(input, output, index=None, col_name=None, cell_val=None, calc=None):
    """Add a column with an optional name and default value at a specific index.
    If a calc function is provided, it will be used to compute the value for each row.
    
    Prepare the test
    
    >>> always_confirm(True)
    >>> make_csv('__test__.csv', [['a', 'b', 'c'], [0, 0, 0], [1, 2, 3]])
    >>> csv_header('__test__.csv')
    ['a', 'b', 'c']
    
    Test for adding at an index
    
    >>> addcolumn('__test__.csv', '__test2__.csv', 1, 'x') # doctest: +ELLIPSIS
    Adding column "x" at index 1 with default value ""
    ...
    >>> csv_header('__test2__.csv')
    ['a', 'x', 'b', 'c']
    
    Test for adding at the end
    
    >>> addcolumn('__test__.csv', '__test2__.csv', col_name="foo", cell_val='asdf') # doctest: +ELLIPSIS
    Adding column "foo" at index 3 with default value "asdf"
    ...
    >>> read_csv('__test2__.csv')
    [['a', 'b', 'c', 'foo'], ['0', '0', '0', 'asdf'], ['1', '2', '3', 'asdf']]
    
    Test for adding a calculated column
    
    >>> addcolumn('__test__.csv', '__test2__.csv', col_name="sum", calc=sum) # doctest: +ELLIPSIS
    Adding calculated column "sum" at index 3
    ...
    >>> read_csv('__test2__.csv')
    [['a', 'b', 'c', 'sum'], ['0', '0', '0', '0'], ['1', '2', '3', '6']]
    
    Clean up
    
    >>> os.remove('__test2__.csv')
    >>> os.remove('__test__.csv')
    """
    
    with open(input, 'rbU') as infile:
        reader = csv.reader(infile)
        
        # need first row for indexing
        header = reader.next()
        
        # figure out where we are adding the column
        if index is None:
            index = len(header)
        
        # what goes in the cells?
        if cell_val is None:
            cell_val = ''
        
        # what goes in the header? by default same as cells
        if col_name is None and calc is None:
            col_name = cell_val
        
        if calc is None:
            print 'Adding column "%s" at index %d with default value "%s"' %(col_name, index, cell_val)
        else:
            print 'Adding calculated column "%s" at index %d' %(col_name, index)
        
        def generator(rowNum, row):
            if rowNum == 0:
                # it is the header
                if calc is not None and col_name is None:
                    _convert_numbers(row)
                    val = calc(row)
                else:
                    val = col_name
                    
                row.insert(index, val)
            else:
                if calc is not None:
                    _convert_numbers(row)
                    val = calc(row)
                else:
                    val = cell_val
                row.insert(index, val)
            return row
        
        write_csv(reader, output, header=header, generator=generator)


def _dropcolumn_process(args):
    return dropcolumn(args.input, args.output, args.index, args.name)

def _dropcolumn_args(parser):
    parser.add_argument('input', metavar="INPUT_CSV", help='A csv file to read from')
    parser.add_argument('output', metavar="OUTPUT_CSV", help='A csv file to write to')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--name', '-n', help='The name of the column to remove')
    group.add_argument('--index', '-i', type=int, help='The position of the column to remove (0-indexed)')
    parser.set_defaults(func=_dropcolumn_process)
        
def dropcolumn(input, output, index=None, col_name=None):
    """Remove a column with a given name or index.
    
    Prepare the test
    
    >>> always_confirm(True)
    >>> make_csv('__test__.csv', [['a', 'b', 'c']])
    >>> csv_header('__test__.csv')
    ['a', 'b', 'c']
    
    Test for removing by index
    
    >>> dropcolumn('__test__.csv', '__test2__.csv', 1) # doctest: +ELLIPSIS
    Dropping column at index 1
    ...
    >>> csv_header('__test2__.csv')
    ['a', 'c']
    
    Test for dropping by name
    
    >>> dropcolumn('__test__.csv', '__test2__.csv', col_name="c") # doctest: +ELLIPSIS
    Dropping column "c" at index 2
    ...
    >>> csv_header('__test2__.csv')
    ['a', 'b']
    
    Test for invalid arguments
    
    >>> dropcolumn('__test__.csv', '__test2__.csv') # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    Exception: One of index and col_name must be specified
    
    Clean up
    
    >>> os.remove('__test2__.csv')
    >>> os.remove('__test__.csv')
    """
    if index is None and col_name is None:
            raise Exception("One of index and col_name must be specified")
        
    with open(input, 'rbU') as infile:
        reader = csv.reader(infile)
        
        header = reader.next()
            
        col_name, index = col_reference(header, col_name, index)
        
        if col_name:
            print 'Dropping column "%s" at index %d' %(col_name, index)
        else:
            print 'Dropping column at index %d' %(index)
        
        def generator(rowNum, row):
            row.pop(index)
            return row
        
        write_csv(reader, output, header=header, generator=generator)

def _rename_process(args):
    return rename(args.input, args.output, args.to, index=args.index, col_name=args.name)

def _rename_args(parser):
    parser.add_argument('input', metavar="INPUT_CSV", help='A csv file to read from')
    parser.add_argument('output', metavar="OUTPUT_CSV", help='A csv file to write to')
    parser.add_argument('--to', help="The new name of the column", required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--name', '-n', help='The name of the column to rename')
    group.add_argument('--index', '-i', type=int, help='The position of the column to rename (0-indexed)')
    parser.set_defaults(func=_rename_process)
        
def rename(input, output, to_name, index=None, col_name=None):
    """Rename a column with a given name or index.
    
    Prepare the test
    
    >>> always_confirm(True)
    >>> make_csv('__test__.csv', [['a', 'b', 'c']])
    >>> csv_header('__test__.csv')
    ['a', 'b', 'c']
    
    Test for renaming by index
    
    >>> rename('__test__.csv', '__test2__.csv', "foo", index=1) # doctest: +ELLIPSIS
    Renaming column at index 1 to "foo"
    ...
    >>> csv_header('__test2__.csv')
    ['a', 'foo', 'c']
    
    Test for renaming by name
    
    >>> rename('__test__.csv', '__test2__.csv', "foo", col_name="a") # doctest: +ELLIPSIS
    Renaming column "a" to "foo"
    ...
    >>> csv_header('__test2__.csv')
    ['foo', 'b', 'c']
    
    
    Test for invalid arguments
    
    >>> rename('__test__.csv', '__test2__.csv', 'foo') # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    Exception: One of index and col_name must be specified
    
    Clean up
    
    >>> os.remove('__test2__.csv')
    >>> os.remove('__test__.csv')
    """
    
    if index is None and col_name is None:
        raise Exception("One of index and col_name must be specified")
    
    with open(input, 'rbU') as infile:
        reader = csv.reader(infile)
        
        header = reader.next()
            
        col_name, index = col_reference(header, col_name, index)
        
        if col_name:
            print 'Renaming column "%s" to "%s"' %(col_name, to_name)
        else:
            print 'Renaming column at index %d to "%s"' %(index, to_name)
        
        def generator(rowNum, row):
            if rowNum == 0:
                # only do anything to the header
                row[index] = to_name
                
            return row
        
        write_csv(reader, output, header=header, generator=generator)

        
def _position_process(args):
    return position(args.input, args.output, index=args.index, col_name=args.name, to_name=args.to)

def _position_args(parser):
    parser.add_argument('input', metavar="INPUT_CSV", help='A csv file to read from')
    parser.add_argument('output', metavar="OUTPUT_CSV", help='A csv file to write to')
    parser.add_argument('--to', type=int, help="The new position of the column", required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--name', '-n', help='The name of the column to position')
    group.add_argument('--index', '-i', type=int, help='The position of the column to position (0-indexed)')
    parser.set_defaults(func=_position_process)
        
def position(input, output, to_index, index=None, col_name=None):
    """Reposition a column with a given name or index.
    The to_index value specifies the position of the column in the final table.
    
    Prepare the test
    
    >>> always_confirm(True)
    >>> make_csv('__test__.csv', [['a', 'b', 'c']])
    >>> csv_header('__test__.csv')
    ['a', 'b', 'c']
    
    Test for positioning by index (and moving to the left)
    
    >>> position('__test__.csv', '__test2__.csv', 0, index=2) # doctest: +ELLIPSIS
    Moving column at index 2 to index 0
    ...
    >>> csv_header('__test2__.csv')
    ['c', 'a', 'b']
    
    Test for positioning by name (and moving to the right)
    
    >>> position('__test__.csv', '__test2__.csv', 1, col_name="a") # doctest: +ELLIPSIS
    Moving column "a" to index 1
    ...
    >>> csv_header('__test2__.csv')
    ['b', 'a', 'c']
    
    Test for invalid arguments
    
    >>> position('__test__.csv', '__test2__.csv', 1) # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    Exception: One of index and col_name must be specified
    
    Clean up
    
    >>> os.remove('__test2__.csv')
    >>> os.remove('__test__.csv')
    """
    
    if index is None and col_name is None:
        raise Exception("One of index and col_name must be specified")
    
    with open(input, 'rbU') as infile:
        reader = csv.reader(infile)
        
        header = reader.next()

        col_name, index = col_reference(header, col_name, index)
        
        if col_name:
            print 'Moving column "%s" to index %d' %(col_name, to_index)
        else:
            print 'Moving column at index %d to index %d' %(index, to_index)
        
        def generator(rowNum, row):
            row.insert(to_index, row.pop(index))
                
            return row
        
        write_csv(reader, output, header=header, generator=generator)
        
def _merge_process(args):
    return merge(args.left, args.right, args.output, args.stop_shorter)

def _merge_args(parser):
    parser.add_argument('left', metavar="LEFT_INPUT_CSV", help='The left input csv table')
    parser.add_argument('right', metavar="RIGHT_INPUT_CSV", help='A right input csv table')
    parser.add_argument('output', metavar="OUTPUT_CSV", help='A csv file to write to')
    parser.add_argument('--stop-shorter', action='store_true', help='Stop whenever the shorter file ends', required=False)
    parser.set_defaults(func=_merge_process)
    
def merge(left, right, output, stop_shorter=False):
    """Combine two tables by adjoining their rows in order
    
    Prepare the test
    
    >>> always_confirm(True)
    >>> make_csv('__test__.csv', [['a', 'b', 'c'], [0, 0, 0], [1, 1, 1]])
    >>> csv_header('__test__.csv')
    ['a', 'b', 'c']
    >>> count_rows('__test__.csv')
    3
    >>> make_csv('__test2__.csv', [['x', 'y'], [0, 0], [1, 1], [2, 2]])
    >>> csv_header('__test2__.csv')
    ['x', 'y']
    >>> count_rows('__test2__.csv')
    4
    
    Test for regular merging
    
    >>> merge('__test__.csv', '__test2__.csv', '__test3__.csv') # doctest: +ELLIPSIS
    Wrote ...
    >>> csv_header('__test3__.csv')
    ['a', 'b', 'c', 'x', 'y']
    >>> count_rows('__test3__.csv')
    4
    
    Test for merging, stopping when the shorter file ends
    
    >>> merge('__test__.csv', '__test2__.csv', '__test3__.csv', stop_shorter=True) # doctest: +ELLIPSIS
    Wrote ...
    >>> csv_header('__test3__.csv')
    ['a', 'b', 'c', 'x', 'y']
    >>> count_rows('__test3__.csv')
    3
    
    Clean up
    
    >>> os.remove('__test3__.csv')
    >>> os.remove('__test2__.csv')
    >>> os.remove('__test__.csv')
    """
    with open(left, 'rbU') as leftfile, open(right, 'rbU') as rightfile:
        leftReader = csv.reader(leftfile)
        rightReader = csv.reader(rightfile)
        
        def generator(rowNum, rows):
            leftRow = [] if rows[0] is None else rows[0]
            rightRow = [] if rows[1] is None else rows[1]
                
            leftRow.extend(rightRow)
            
            return leftRow
            
        if stop_shorter:
            iterator = itertools.izip(leftReader, rightReader)
        else:
            iterator = itertools.izip_longest(leftReader, rightReader)
            
        write_csv(iterator, output, generator=generator)

def _select_process(args):
    return select(args.input, args.output, args.from_, args.to)

def _select_args(parser):
    parser.add_argument('input', metavar="INPUT_CSV", help='A csv file to read from')
    parser.add_argument('output', metavar="RIGHT_OUTPUT_CSV", help='A csv file to write the right columns to')
    parser.add_argument('--from', dest="from_", metavar="FROM_INDEX", type=int, help='The column to start with (default 0)')
    parser.add_argument('--to', metavar="TO_INDEX", type=int, help='The column to end with, inclusive (default last)')
    parser.set_defaults(func=_select_args)
        
def select(input, output, fromIndex=None, toIndex=None):
    """Select a subset of the columns by index range
    
    Prepare the test
    
    >>> always_confirm(True)
    >>> make_csv('__test__.csv', [['a', 'b', 'c']])
    >>> csv_header('__test__.csv')
    ['a', 'b', 'c']
    
    Test select with both ends specified
    
    >>> select('__test__.csv', '__test2__.csv', 1, 3) # doctest: +ELLIPSIS
    Selecting columns 1 through 2
    ...
    >>> csv_header('__test2__.csv')
    ['b', 'c']
    
    Test select with only start specified
    
    >>> select('__test__.csv', '__test2__.csv', fromIndex=2) # doctest: +ELLIPSIS
    Selecting columns 2 through 2
    ...
    >>> csv_header('__test2__.csv')
    ['c']
    
    Test select with only stop specified
    >>> select('__test__.csv', '__test2__.csv', toIndex=2) # doctest: +ELLIPSIS
    Selecting columns 0 through 1
    ...
    >>> csv_header('__test2__.csv')
    ['a', 'b']
    
    Clean up
    
    >>> os.remove('__test2__.csv')
    >>> os.remove('__test__.csv')
    """
    
    with open(input, 'rbU') as infile:
        reader = csv.reader(infile)
        
        header = reader.next()
        fromIndex = 0 if fromIndex is None else fromIndex
        toIndex = len(header) if toIndex is None else toIndex
        
        print 'Selecting columns %d through %d' %(fromIndex, toIndex - 1)
        
        def generator(rowNum, row):
            return row[fromIndex:toIndex]
            
        write_csv(reader, output, header=header, generator=generator)

        
    
if __name__ == '__main__':
    import argparse
    
    # create the top-level parser
    parser = argparse.ArgumentParser(description="Perform operations on CSV files")
    parser.add_argument('--yes', action='store_true', help='Answer yes to all prompts')
    subparsers = parser.add_subparsers(metavar="COMMAND")
    
    # create the parser for the "addcolumn" command
    addcolumn_parser = subparsers.add_parser('addcolumn', help='insert a column')
    _addcolumn_args(addcolumn_parser)
    
    # create the parser for the "rename" command
    rename_parser = subparsers.add_parser('rename', help='rename a column')
    _rename_args(rename_parser)
    
    # create the parser for the "position" command
    position_parser = subparsers.add_parser('position', help='reposition a column')
    _position_args(position_parser)
    
    # create the parser for the "dropcolumn" command
    dropcolumn_parser = subparsers.add_parser('dropcolumn', help='remove a column')
    _dropcolumn_args(dropcolumn_parser)

    # create the parser for the "merge" command
    merge_parser = subparsers.add_parser('merge', help='vertically merge two tables')
    _merge_args(merge_parser)
    
    # create the parser for the "select" command
    select_parser = subparsers.add_parser('select', help='select columns from a table, by index')
    _select_args(select_parser)
    
    args = parser.parse_args()
    
    if not args.yes:
        always_confirm(False)
    
    args.func(args)
