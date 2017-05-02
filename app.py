import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
import imghdr
from PIL import Image
from huffman import make_freq_table, make_tree
import sys
import util

# Initialize the Flask application
app = Flask(__name__)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
	# Get the name of the uploaded file
	file = request.files['file']
	# Check if the file is one of the allowed types/extensions
	if file and allowed_file(file.filename):
		# Make the filename safe, remove unsupported chars
		filename = secure_filename(file.filename)
		# Move the file form the temporal folder to
		# the upload folder we setup
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		file_in = './uploads/' + filename
		#process checkbox value
		value=request.form['checkbox']
		if value == 'PIL':
			compress_PIL(file_in, 1)
			file_out = get_outfile_pil(filename)
			file_out = './uploads/' + file_out
			return render_template('upload.html', file_in=file_in, file_out=file_out)
		elif value == "Huffman":
			print(file_in)
			huffman(file_in)
			file_out = filename + '.huf'
			return render_template('upload.html', file_in=file_in, file_out=file_out)
		elif value == 'rle':
			return render_template('upload.html', file_in=file_in)
		else:
			return render_template('index.html')


################################################
# all def here is get the name of file compress#

def get_outfile_pil(infile):
	baseName, e = os.path.splitext(infile)
	f, e = os.path.splitext(infile)
	f = (baseName + str("_compress"))
	outfile = f + ".jpg"
	return outfile


################################################
# File compressing by compress_PIL(path_file, 1)
def compress_PIL(infile, times):
	baseName, e = os.path.splitext(infile)
	try:
		f, e = os.path.splitext(infile)
		f = (baseName + str("_compress"))
		# outfile = f + ".png"
		outfile = f + ".jpg"
		#open previously generated file
		compImg = Image.open(infile)
		#compress file at 20% of previous quality
		# compImg.save(outfile, "PNG", quality=20)
		compImg.save(outfile, "JPEG", quality=20)
	except IOError:
		print("Cannot convert", infile)


# Algorithm for compressing image
def huffman(infile):
    with open(infile, 'rb') as uncompressed:
        freqs = make_freq_table(uncompressed)
        tree = make_tree(freqs)
        uncompressed.seek(0)
        with open(infile+'.huf', 'wb') as compressed:
            util.compress(tree, uncompressed, compressed)


#def rle(infile):
#    return outfile


@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'],
							   filename)


if __name__ == '__main__':
	app.run(
		host="0.0.0.0",
		port=int("8080"),
		debug=True
	)
