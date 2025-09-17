import requests
import sys

apple = "https://newsapi.org/v2/everything?q=apple&from=2025-09-16&to=2025-09-16&sortBy=popularity&apiKey=cc18a309ccc94c5a9d1f88d27fefd470"
tesla = "https://newsapi.org/v2/everything?q=tesla&from=2025-08-17&sortBy=publishedAt&apiKey=cc18a309ccc94c5a9d1f88d27fefd470"
us = "https://newsapi.org/v2/top-headlines?country=us&category=business&apiKey=cc18a309ccc94c5a9d1f88d27fefd470"
techCrunch = "https://newsapi.org/v2/top-headlines?sources=techcrunch&apiKey=cc18a309ccc94c5a9d1f88d27fefd470"
wallStreet = "https://newsapi.org/v2/everything?domains=wsj.com&apiKey=cc18a309ccc94c5a9d1f88d27fefd470"

apis = {
    1: ("Apple yesterday", apple),
    2: ("Tesla last month", tesla),
    3: ("Top business headlines US", us),
    4: ("Top headlines TechCrunch", techCrunch),
    5: ("The Wall Street Journal last 6 months", wallStreet)
}

def show_articles(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Error fetching data:", response.status_code, response.text)
        return
    
    data = response.json()
    articles = data.get("articles", [])
    if not articles:
        print("No articles found.")
        return
    
    index = 0
    while True:
        a = articles[index]
        print("\n" + "-" * 80)
        print(f"({index+1}/{len(articles)})")
        print(f"Title: {a.get('title', 'N/A')}\n")
        print(f"Description: {a.get('description', 'N/A')}\n")
        print(f"Content: {a.get('content', 'N/A')}\n")
        print(f"Published At: {a.get('publishedAt', 'N/A')}")
        print(f"Source: {a.get('source', {}).get('name', 'N/A')}")
        print(f"URL: {a.get('url', 'N/A')}")
        print("-" * 80)

        action = input("Type 'next', 'prev', 'back' or 'exit': ").strip().lower()
        if action == "next":
            if index < len(articles) - 1:
                index += 1
            else:
                print("No more articles.")
        elif action == "prev":
            if index > 0:
                index -= 1
            else:
                print("This is the first article.")
        elif action == "back":
            break
        elif action == "exit":
            print("Goodbye!")
            sys.exit()
        else:
            print("Invalid choice.")

def main():
    while True:
        print("\nNews today! Choose an option:")
        for key, (name, _) in apis.items():
            print(f"{key}. {name}")
        print("6. Exit")

        try:
            usr = int(input("Enter your choice: "))
        except ValueError:
            print("Please enter a number.")
            continue

        if usr == 6:
            print("Goodbye!")
            break
        elif usr in apis:
            _, url = apis[usr]
            show_articles(url)
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
