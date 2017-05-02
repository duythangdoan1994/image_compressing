# The functions in this file are to be implemented by students.
"""
Huffman Encoder and Decoder
by: Vishal Patel & Rizwan Qureshi - EB2

Description: This program compresses and decompresses files using Huffman
codes. The compress feature is separated as a command line utility where
a user can use the $python3 ../compress.py (filename).(extension) command in
the wwwroot directory to compress a file into a .huf extension. The decompress
feature is used by the web server when run using $python3 ../webserver.py and
the address http://localhost:8000/(filename).(extension) in a browser to
display the file.

To use compress: 1. Ensure the file to be compressed is in the wwwroot
directory.
2. Use the $python3 ../compress.py (filename).(extension) command

To view file: 1. Start server using the $python3 ../webserver.py command.
2. Go to the address http://localhost:8000/(filename).(extension) in a browser.
3. The file should display within the web browser.

Additional Info: The functions in the util.py file was completed.
- Included pictures: huffman.bmp, cat.jpg
"""
import bitio
import huffman


def read_tree(bitreader):
    '''Read a description of a Huffman tree from the given bit reader,
    and construct and return the tree. When this function returns, the
    bit reader should be ready to read the next bit immediately
    following the tree description.

    Huffman trees are stored in the following format:
      * TreeLeafEndMessage is represented by the two bits 00.
      * TreeLeaf is represented by the two bits 01, followed by 8 bits
          for the symbol at that leaf.
      * TreeBranch is represented by the single bit 1, followed by a
          description of the left subtree and then the right subtree.

    Args:
      bitreader: An instance of bitio.BitReader to read the tree from.

    Returns:
      A Huffman tree constructed according to the given description.
    '''
    tree_dict = {  # maps the bit sequence to the tree instance
        '00': huffman.TreeLeafEndMessage(),
        '01': lambda i: huffman.TreeLeaf(i),
        '1': lambda l, r: huffman.TreeBranch(l, r)
    }

    b1 = bitreader.readbit()  # read first bit
    if b1 == 1:  # if first bit is a 1 it must be a branch
        left = read_tree(bitreader)  # apply recursively over left and right
        right = read_tree(bitreader) # branch
        tree = tree_dict['1'](left, right)
    else:  # otherwise its either a endLeaf or valueLeaf
        b2 = bitreader.readbit()
        b = b1 + b2
        if b == 0:
            tree = tree_dict['00']
        elif b == 1:
            tree = tree_dict['01'](bitreader.readbits(8))
    # print(tree)
    return tree


def decompress(compressed, uncompressed):
    '''First, read a Huffman tree from the 'compressed' stream using your
    read_tree function. Then use that tree to decode the rest of the
    stream and write the resulting symbols to the 'uncompressed'
    stream.

    Args:
      compressed: A file stream from which compressed input is read.
      uncompressed: A writable file stream to which the uncompressed
          output is written.

    '''
    bitstream = bitio.BitReader(compressed)  # Gets bits from compressed
    tree = read_tree(bitstream)  # Produce tree based on bit sequence
    while True:  # Do final decoding of tree based on remaining bits
        val = huffman.decode(tree, bitstream)
        if val is None:  # Stop at endLead
            break
        else:  # Write the stored values in the tree (ordered by bit sequence)
            uncompressed.write(bytes([val]))  # as a byte in uncompressed


def write_tree(tree, bitwriter):
    '''Write the specified Huffman tree to the given bit writer.  The
    tree is written in the format described above for the read_tree
    function.

    DO NOT flush the bit writer after writing the tree.

    Args:
      tree: A Huffman tree.
      bitwriter: An instance of bitio.BitWriter to write the tree to.
    '''
    if type(tree) is huffman.TreeBranch:
        # Indicate branch
        bitwriter.writebit(1)

        write_tree(tree.left, bitwriter)  # Recurse over left and right branch
        write_tree(tree.right, bitwriter)
    elif type(tree) is huffman.TreeLeaf:
        # Indicate leaf
        bitwriter.writebit(0)
        bitwriter.writebit(1)

        binValue = "{0:b}".format(tree.value)  # Get binary value

        # Pad front with zeros to get 8 bit binary value
        for _ in range(8-len(binValue)):
            bitwriter.writebit(0)

        # Print the value in binary
        for bit in binValue:
            if bit == "1":
                bitwriter.writebit(1)
            else:
                bitwriter.writebit(0)

    elif type(tree) is huffman.TreeLeafEndMessage:
        # Indicate end message
        bitwriter.writebit(0)
        bitwriter.writebit(0)


def compress(tree, uncompressed, compressed):
    '''First write the given tree to the stream 'compressed' using the
    write_tree function. Then use the same tree to encode the data
    from the input stream 'uncompressed' and write it to 'compressed'.
    If there are any partially-written bytes remaining at the end,
    write 0 bits to form a complete byte.

    Args:
      tree: A Huffman tree.
      uncompressed: A file stream from which you can read the input.
      compressed: A file stream that will receive the tree description
          and the coded input data.
    '''
    bitstream = bitio.BitWriter(compressed)
    write_tree(tree, bitstream)

    enc_table = huffman.make_encoding_table(tree)  # Create encoding table
    end_char = enc_table[None]  # Get end char

    input_stream = uncompressed.read(1)  # Read inn one byte

    while input_stream:

        input_char = ord(input_stream)  # Convert to binary
        compressed_char = enc_table[input_char]  # Get compressed byte

        for bit in compressed_char:  # Print the compressed byte
            if bit:
                bitstream.writebit(1)
            else:
                bitstream.writebit(0)

        input_stream = uncompressed.read(1)  # Read the next byte

    # Print end bit
    for bit in end_char:
        if bit:
            bitstream.writebit(1)
        else:
            bitstream.writebit(0)

    bitstream.flush()
