import sys
import os

# Ensure root directory is in python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.services.llm.chat import ask_codebase

def main():
    print("=" * 60)
    print("🤖 DevMindAI Local Codebase Chat (Type 'exit' or 'quit' to stop)")
    print("=" * 60)
    
    while True:
        try:
            query = input("\n💬 Enter question: ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
                
            response = ask_codebase(query)
            print("\n🤖 AI Response:")
            print("-" * 40)
            print(response)
            print("-" * 40)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()