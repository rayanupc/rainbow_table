import hashlib       # Used for SHA-1 hashing
import random        # Used to generate random passwords
import string        # Provides string constants like ascii_lowercase
import json          # Used to read/write JSON files
import sys           # For command-line arguments
import os            # To check if a file exists

# Function to compute SHA-1 hash of a given text
def sha1_hash(text):
    return hashlib.sha1(text.encode()).hexdigest()

# Reduction function: converts a hash into a password candidate
def reduce_function(hash_str, round_num, charset, pw_length):
    # Determines where to extract a portion of the hash
    pos = (round_num * 2) % (len(hash_str) - 8)
    # Converts 8 hex characters into an integer   
    int_val = int(hash_str[pos:pos + 8], 16)      
    pwd = ''
    # Builds a password of desired length
    for _ in range(pw_length):                   
        pwd += charset[int_val % len(charset)]   
        int_val //= len(charset)                 
    return pwd

# Generates a rainbow table and stores it as a JSON file
def generate_table(charset, pw_length, chain_length, nb_chains, table_path):
    table = {}
    for _ in range(nb_chains):
        # Generates a random start password
        start = ''.join(random.choices(charset, k=pw_length))  
        pwd = start
        # Builds the chain of password -> hash -> password -> hash -> ... 
        for i in range(chain_length):                          
            hashed = sha1_hash(pwd)                            
            pwd = reduce_function(hashed, i, charset, pw_length)  
        end_hash = sha1_hash(pwd)                              
        # Store end_hash -> start password
        table[end_hash] = start                                
    with open(table_path, 'w') as f:
        # Save table to json file
        json.dump(table, f)                                    
    print(f"[+] Table stored in {table_path}")

# Attempts to crack a hash using a rainbow table
def crack_hash(hash_target, table_path, charset, pw_length, chain_length):
    if not os.path.exists(table_path):
        print("[-] Table not found.")
        return
    with open(table_path, 'r') as f:
        table = json.load(f)
    # Try from last round to first                                   
    for i in reversed(range(chain_length)):                    
        temp_hash = hash_target
        # Reconstruct possible chain
        for j in range(i, chain_length):                       
            pwd = reduce_function(temp_hash, j, charset, pw_length)
            temp_hash = sha1_hash(pwd)
        if temp_hash in table:    
            # Get original start password                             
            pwd = table[temp_hash]  
            # Reconstruct the chain                           
            for k in range(chain_length):                      
                # Check if it matches the target hash
                if sha1_hash(pwd) == hash_target:              
                    print(f"[+] Password found : {pwd}")
                    return
                pwd = reduce_function(sha1_hash(pwd), k, charset, pw_length)
    print("[-] Password not found on the table.")

def usage():
    print("Usage :")
    print("  Generate a table : python3 rainbow.py generate <table.json>")
    print("  Cracking a hash   : python3 rainbow.py crack <hash> <table.json>")

# Main program 
if __name__ == "__main__":
    # Set of characters to use in passwords
    charset = string.ascii_lowercase  
    # Length of each password (3 for our demonstration)     
    pw_length = 3   
    # Number of hash-reduction steps per chain                      
    chain_length = 100 
    # Total number of chains in the table                   
    nb_chains = 20000                     

    if len(sys.argv) < 3:
        usage()
    elif sys.argv[1] == "generate":        
        table_file = sys.argv[2]
        generate_table(charset, pw_length, chain_length, nb_chains, table_file)
    elif sys.argv[1] == "crack":          
        if len(sys.argv) != 4:
            usage()
        else:
            hash_input = sys.argv[2]
            table_file = sys.argv[3]
            crack_hash(hash_input, table_file, charset, pw_length, chain_length)
    else:
        usage()
