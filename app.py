import redis
import sys

# Σύνδεση με το Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def main():
    username = input("Εισάγετε το username σας: ")
    
    while True:
        print("\n--- Μενού Redis Movies ---")
        print("(I)nsert Artist | (Q)uery | (S)tatistics | e(X)it")
        choice = input("Επιλογή: ").upper()
        
        if choice == 'I':
            # TODO: Υλοποίηση εισαγωγής ταινίας
            pass
        elif choice == 'Q':
            # TODO: Υλοποίηση αναζήτησης
            pass
        elif choice == 'S':
            # TODO: Υλοποίηση στατιστικών
            pass
        elif choice == 'X':
            print("Έξοδος...")
            break
        else:
            print("Μη έγκυρη επιλογή.")

if __name__ == "__main__":
    main()

