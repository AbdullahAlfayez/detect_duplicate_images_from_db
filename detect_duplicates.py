#Abdullah - twitter: techn_new
# import the necessary packages

from imutils import paths
import numpy as np
import argparse
import cv2
import os
import pyodbc



def dhash(image, hashSize=8):
	# convert the image to grayscale and resize the grayscale image,
	# adding a single column (width) so we can compute the horizontal
	# gradient
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	resized = cv2.resize(gray, (hashSize + 1, hashSize))

	# compute the (relative) horizontal gradient between adjacent
	# column pixels
	diff = resized[:, 1:] > resized[:, :-1]

	# convert the difference image to a hash and return it
	return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])


def hash_images():

        print("[INFO] computing image hashes...")
        imagePaths = list(paths.list_images(args["dataset"]))
        hashes = {}
        print("HEREHRE")
        # loop over our image paths
        for imagePath in imagePaths:
                # load the input image and compute the hash
                image = cv2.imread(imagePath)
                h = dhash(image)

                # grab all image paths with that hash, add the current image
                # path to it, and store the list back in the hashes dictionary
                p = hashes.get(h, [])
                p.append(imagePath)
                hashes[h] = p

        # loop over the image hashes
        for (h, hashedPaths) in hashes.items():
                # check to see if there is more than one image with the same hash
                if len(hashedPaths) > 1:
                        # check to see if this is a dry run
                        if args["remove"] <= 0:
                                # initialize a montage to store all images with the same
                                # hash
                                montage = None

                                # loop over all image paths with the same hash
                                for p in hashedPaths:
                                        # load the input image and resize it to a fixed width
                                        # and height
                                        image = cv2.imread(p)
                                        image = cv2.resize(image, (150, 150))

                                        # if our montage is None, initialize it
                                        if montage is None:
                                                montage = image

                                        # otherwise, horizontally stack the images
                                        else:
                                                montage = np.hstack([montage, image])

                                # show the montage for the hash
                                print("[INFO] hash: {}".format(h))
                                cv2.imshow("Montage", montage)
                                cv2.waitKey(0)

                        # otherwise, we'll be removing the duplicate images
                        else:
                                # loop over all image paths with the same hash *except*
                                # for the first image in the list (since we want to keep
                                # one, and only one, of the duplicate images)
                                for p in hashedPaths[1:]:
                                        os.remove(p)

def process_image(connection, row):

        imageByte = cv2.imdecode(np.fromstring(row.Content, np.uint8), cv2.IMREAD_COLOR)
        image_shape = imageByte.shape
        image_height = image_shape[0]
        image_width = image_shape[1]
        imageByte = imageByte[0:(image_height - 300), 0:image_width]

        cv2.imwrite("{0}\\image_{1}.jpeg".format(folder, row.MediaId), imageByte)
        print("Photo was saved to the folder!!")

        
def get_sitevisit_blob(connection_prd):

    print("Fetching Image...")
    sql1 = "select top(1000) from table .. query" 
    cursor = connection_prd.cursor()
    cursor.execute(sql1)
    rows = cursor.fetchall()
    print("images fetched")
    print(type(rows))
    hash_images()

        
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()

ap.add_argument("-d", "--dataset", required=True,
	help="path to input dataset")
args = vars(ap.parse_args())

folder = "C:\\Users\\user\\Desktop\\detect_duplicate_images_from_db\\Data"



#print("Creating prd connection...")
connection_prd = pyodbc.connect("DRIVER={{SQL Server}};SERVER={0}; database={1}; trusted_connection=no;UID={2};PWD={3}".format("00.00.00.00","databaseName","userName","password"))
print("Connection created.")


try:
    get_blob(connection_prd)
    hash_images()
except Exception as ex:
    connection_prd.rollback()
    print("Excepton is: ")
    print(ex)
    print("Failed to save image to folder ")
finally:
    #closing database connection.
    connection_prd.cursor().close()
    connection_prd.close()
    print("connections are closed")



    
