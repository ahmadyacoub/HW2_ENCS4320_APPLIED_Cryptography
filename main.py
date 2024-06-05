"""
Author: Ahmad Ismail
Date: Jun 5th 2024 
Description: This script demonstrates image encryption and decryption using the TEA (Tiny Encryption Algorithm) in both ECB (Electronic Codebook) and CBC (Cipher Block Chaining) modes
"""
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os

# Constants that Used in TEA algorithim

DELTA = 0x9E3779B9
SUM_INIT = DELTA << 5

# TEA encryption function

def tea_encrypt(plaintext, key):
    # encrypts a 64-bit plaintext block using a 128-bit key with the TEA algorithm
    L, R = plaintext
    sum = 0
    for _ in range(32):
        sum = (sum + DELTA) & 0xFFFFFFFF
        L = (L + (((R << 4) + key[0]) ^ (R + sum) ^ ((R >> 5) + key[1]))) & 0xFFFFFFFF
        R = (R + (((L << 4) + key[2]) ^ (L + sum) ^ ((L >> 5) + key[3]))) & 0xFFFFFFFF
    return L, R

def tea_decrypt(ciphertext, key):
    L, R = ciphertext
    sum = SUM_INIT
    for _ in range(32):
        R = (R - (((L << 4) + key[2]) ^ (L + sum) ^ ((L >> 5) + key[3]))) & 0xFFFFFFFF
        L = (L - (((R << 4) + key[0]) ^ (R + sum) ^ ((R >> 5) + key[1]))) & 0xFFFFFFFF
        sum = (sum - DELTA) & 0xFFFFFFFF
    return L, R
# using 0xFFFFFFFF in TEA encryption helps ensure that all operations are restricted to 32 bits

def xor_block(block1, block2):
    #  XORs two 64 bits together used in CBC mode
    return (block1[0] ^ block2[0], block1[1] ^ block2[1])


def tea_cbc_encrypt(plaintext_blocks, key, initialization_vector):
    # encrypts a list of plaintext blocks using TEA-CBC TEA algorithim in CBC mode

    ciphertext_blocks = []
    prev_block = initialization_vector

    for block in plaintext_blocks:
        block = xor_block(block, prev_block)
        encrypted_block = tea_encrypt(block, key)
        ciphertext_blocks.append(encrypted_block)
        prev_block = encrypted_block

    return ciphertext_blocks


def tea_cbc_decrypt(ciphertext_blocks, key, initialization_vector):
     # decrypts a list of plaintext blocks using TEA-CBC TEA algorithim in CBC mode

    plaintext_blocks = []
    prev_block = initialization_vector

    for block in ciphertext_blocks:
        decrypted_block = tea_decrypt(block, key)
        plaintext_block = xor_block(decrypted_block, prev_block)
        plaintext_blocks.append(plaintext_block)
        prev_block = block

    return plaintext_blocks


def tea_ecb_encrypt(plaintext_blocks, key):
     # encrypts a list of plaintext blocks using TEA-ECB TEA algorithim in ECB mode
    ciphertext_blocks = []

    for block in plaintext_blocks:
        encrypted_block = tea_encrypt(block, key)
        ciphertext_blocks.append(encrypted_block)

    return ciphertext_blocks

def tea_ecb_decrypt(ciphertext_blocks, key):
     # decrypts a list of plaintext blocks using TEA-ECB TEA algorithim in ECB mode
    plaintext_blocks = []

    for block in ciphertext_blocks:
        decrypted_block = tea_decrypt(block, key)
        plaintext_blocks.append(decrypted_block)

    return plaintext_blocks

def image_to_blocks(image):
    # converts an image to a list of 64-bit blocks
    pixels = np.array(image)
    shape = pixels.shape
    blocks = []

    flat_pixels = pixels.flatten()
    if len(flat_pixels) % 8 != 0:
        flat_pixels = np.pad(flat_pixels, (0, 8 - len(flat_pixels) % 8), 'constant')

    for i in range(0, len(flat_pixels), 8):
        block = flat_pixels[i:i+8]
        L = int.from_bytes(block[:4], byteorder='big')
        R = int.from_bytes(block[4:], byteorder='big')
        blocks.append((L, R))

    return blocks, shape

def blocks_to_image(blocks, shape):
    # converts a list of 64bit blocks back to an image
    flat_pixels = []
    for block in blocks:
        flat_pixels.extend(block[0].to_bytes(4, byteorder='big'))
        flat_pixels.extend(block[1].to_bytes(4, byteorder='big'))
    pixels = np.array(flat_pixels).reshape(shape)
    return Image.fromarray(pixels.astype('uint8'))

def main():
    # main function to encrypt and decrypt an image using TEA-CBC & TEA-EBC

    # input path for the image
    
    
    image_input = input("Enter the path of the image file: ")

    # check if the file exists
    
    if not os.path.isfile(image_input):
        print(f"Error: The file at path {image_input} does not exist.")
        return

    try:
        # load the image from the file system
        image = Image.open(image_input)
    except IOError:
        print("Error: Unable to open the image file.")
        return

    # convert to grayscale
    image = image.convert("L")

    # display the original image
    plt.imshow(image, cmap='gray')
    plt.title("Original Image")
    plt.axis('off')
    plt.show()

    image_blocks, image_shape = image_to_blocks(image)

    # get user input for the key
    key_input = input("Enter the key as four 32-bit hexadecimal numbers separated by spaces (e.g., 0xDDEEFF00 0x55667788 0x55667788 0xDDEEFF00): ")
    try:
        key = [int(x, 16) for x in key_input.split()]
        if len(key) != 4:
            raise ValueError
    except ValueError:
        print("Error: Invalid key format ! ")
        return

    # get user input for the IV
    initialization_vector_input = input("Enter the initialization_vector (IV) as two 32-bit hexadecimal numbers separated by a space (e.g., 0xDDEEFF00 0xEEFF0011): ")
    try:
        initialization_vector = tuple(int(x, 16) for x in initialization_vector_input.split())
        if len(initialization_vector) != 2:
            raise ValueError
    except ValueError:
        print("Error: Invalid IV format.")
        return

    # encrypt and Decrypt the Image Using ECB Mode
    try:
        # encrypt using ECB mode
        ciphertext_blocks_ecb = tea_ecb_encrypt(image_blocks, key)

        # display the encrypted image (ECB)
        encrypted_image_ecb = blocks_to_image(ciphertext_blocks_ecb, image_shape)
        plt.imshow(encrypted_image_ecb, cmap='gray')
        plt.title("Encrypted Image (ECB) -Ahmad Ismail 1202450-")
        plt.axis('off')
        plt.show()

        # decrypt using ECB mode
        decrypted_blocks_ecb = tea_ecb_decrypt(ciphertext_blocks_ecb, key)

        # convert blocks back to image
        decrypted_image_ecb = blocks_to_image(decrypted_blocks_ecb, image_shape)

        # display the decrypted image
        plt.imshow(decrypted_image_ecb, cmap='gray')
        plt.title("Decrypted Image (ECB) -Ahmad Ismail 1202450-")
        plt.axis('off')
        plt.show()
    except Exception as e:
        print(f"Error during ECB encryption/decryption: {e}")
        return

    # encrypt and Decrypt the Image Using CBC Mode
    try:
        # encrypt using CBC mode
        ciphertext_blocks_cbc = tea_cbc_encrypt(image_blocks, key, initialization_vector)

        # display the encrypted image (CBC)
        encrypted_image_cbc = blocks_to_image(ciphertext_blocks_cbc, image_shape)
        plt.imshow(encrypted_image_cbc, cmap='gray')
        plt.title("Encrypted Image (CBC) -Ahmad Ismail 1202450-")
        plt.axis('off')
        plt.show()

        # decrypt using CBC mode
        decrypted_blocks_cbc = tea_cbc_decrypt(ciphertext_blocks_cbc, key, initialization_vector)

        # convert blocks back to image
        decrypted_image_cbc = blocks_to_image(decrypted_blocks_cbc, image_shape)

        # display the decrypted image
        plt.imshow(decrypted_image_cbc, cmap='gray')
        plt.title("Decrypted Image (CBC) -Ahmad Ismail 1202450-")
        plt.axis('off')
        plt.show()
    except Exception as e:
        print(f"Error during CBC encryption/decryption: {e}")
        return

# to call main function and start the code
if __name__ == "__main__":
    main()

