import streamlit as st
import requests
import pandas as pd
import json
import matplotlib.pyplot as plt
import pymysql

api_key = "your API key"  #paste ur API key here
#connect to ur  
try:
    mydb = pymysql.connect(
        host = "localhost",
        user = "root",  #use port if connecting to cloud server
        password = "your password",
        database = "your database")
    cursor = mydb.cursor()
    st.session_state.mydb = mydb
except pymysql.Error as err:
    st.error(f"Database connection error: {err}")
    st.stop()


#create temporary table to store current page datas to visualise them 
def create_temp_table(data_list):
  try:
      cursor.execute("""
          CREATE TEMPORARY TABLE temp_books (
              book_id VARCHAR(255),
              search_key VARCHAR(255),
              book_title VARCHAR(500),
              book_subtitle TEXT,
              book_authors TEXT,
              book_description TEXT,
              industryIdentifiers TEXT,
              text_readingModes BOOLEAN,
              image_readingModes BOOLEAN,
              pageCount INT,
              categories TEXT,
              language VARCHAR(50),
              imageLinks TEXT,
              ratingsCount INT,
              averageRating FLOAT,
              country VARCHAR(50),
              saleability VARCHAR(50),
              isEbook BOOLEAN,
              amount_listPrice FLOAT,
              currencyCode_listPrice VARCHAR(10),
              amount_retailPrice FLOAT,
              currencyCode_retailPrice VARCHAR(10),
              buyLink TEXT,
              year VARCHAR(4),
              publisher TEXT
          );
      """)
      insert_values = [tuple(d.values()) for d in data_list]
      cursor.executemany("""
          INSERT INTO temp_books (book_id, search_key, book_title, book_subtitle, book_authors, book_description,
                    industryIdentifiers, text_readingModes, image_readingModes, pageCount, categories,
                    language, imageLinks, ratingsCount, averageRating, country, saleability, isEbook,
                    amount_listPrice, currencyCode_listPrice, amount_retailPrice, currencyCode_retailPrice, buyLink, year, publisher)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
      """, insert_values)
      mydb.commit()
  except pymysql.Error as err:
        st.error(f"Database error: {err}")

#drop temporary table
def drop_temp_table():
    """Drops the temporary table after analysis."""
    cursor.execute("DROP TEMPORARY TABLE temp_books;")
    mydb.commit()

# Function for Question 1: Check Availability of eBooks vs Physical Books
def check_ebook_availability(data_list):
    create_temp_table(data_list)
    query = """
        SELECT isEbook, COUNT(*) AS book_count
        FROM temp_books
        GROUP BY isEbook;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["isEbook", "book_count"])
    df.index = df.index + 1
    st.dataframe(df)
    st.write("")

    #create graphs
    fig, ax = plt.subplots()  
    bars = ax.bar(df["isEbook"], df["book_count"], color=['blue', 'lightcoral'])
    ax.set_facecolor('lightgray')  
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height , height,ha='center', va='bottom')

    ax.set_title("Availability of eBooks vs Physical Books",color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.1'))
    ax.set_xlabel("Book Format",color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))
    ax.set_ylabel("Number of Books",color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))
    ax.set_xticks([0, 1]) 
    ax.set_xticklabels(["Physical Book", "eBook"])
    ax.title.set_position([0.5, 1.1])
    plt.subplots_adjust(top=0.9)
    st.pyplot(fig)

    drop_temp_table()

# Function for Question 2: Find the Publisher with the Most Books Published
def publisher_most_books(data_list):
    create_temp_table(data_list)
    query = """
        SELECT publisher, COUNT(*) AS book_count
        FROM temp_books
        GROUP BY publisher
        ORDER BY book_count DESC
        LIMIT 2;  -- Fetch the top 2 publishers
    """
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["Publisher", "Book Count"])
    df.index = df.index + 1
    #if unknown publisher is in top,lets print the 2nd value to show the real top publisher apart from unknown publisher
    #we cant ignore unknown publisher as well
    #because what if the unknown publishers has a common publisher and has more published books
    if df.loc[1, "Publisher"] == "Unknown Publisher":
        st.dataframe(df)
    else:
        st.dataframe(df.head(1))
    st.write("")

    if df.loc[1, "Publisher"] == "Unknown Publisher":
        fig, ax = plt.subplots()  
        bars = ax.bar(df["Publisher"], df["Book Count"], color=['blue', 'lightcoral'])
        ax.set_facecolor('lightgray')  
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height , height,ha='center', va='bottom')

        ax.set_title("Number of Books Published by Publisher",color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.1'))
        ax.set_xlabel("Publisher",color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))
        ax.set_ylabel("Book Count",color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))
        ax.set_xticks([0, 1])
        ax.set_xticklabels(df["Publisher"].tolist())
        ax.title.set_position([0.5, 1.05])
        plt.subplots_adjust(top=0.9)
        st.pyplot(fig)
    else:
        fig, ax = plt.subplots()
        bars = ax.bar(df.loc[1, "Publisher"], df.loc[1, "Book Count"], color='blue')
        ax.set_facecolor('lightgray')  
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height , height,ha='center', va='bottom')

        ax.set_title("Number of Books Published by Publisher",color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.1'))
        ax.set_xlabel("Publisher",color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))
        ax.set_ylabel("Book Count",color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))
        ax.set_xticks([0]) 
        ax.set_xticklabels([df.loc[1, "Publisher"]])
        ax.title.set_position([0.5, 1.1])
        plt.subplots_adjust(top=0.9)
        st.pyplot(fig)

    drop_temp_table()


# Function for Question 3: Identify the Publisher with the Highest Average Rating
def publisher_highest_avg_rating_overall(data_list):
    create_temp_table(data_list)
    query = """
        SELECT publisher, AVG(averageRating) AS avg_rating
        FROM temp_books
        GROUP BY publisher
        ORDER BY avg_rating DESC
        LIMIT 1;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["Publisher", "Average Rating"])
    df.index = df.index + 1
    st.dataframe(df)
    st.write("")

    fig, ax = plt.subplots(figsize=(1, 2)) 
    bars = ax.bar(df["Publisher"], df["Average Rating"], color=['yellow'])
    ax.set_facecolor('lightgray') 
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height , height,ha='center', va='bottom',fontsize=6)

    ax.set_title("Average Rating of Books by Publisher",fontsize=8,color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.1'))
    ax.set_xlabel("Publisher",fontsize=6,color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))
    ax.set_ylabel("Average Rating",fontsize=6,color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))
    ax.set_xticks([0]) 
    ax.set_xticklabels(df["Publisher"].tolist(),fontsize=6)
    ax.title.set_position([0.5, 1.1])
    plt.subplots_adjust(top=0.9)
    st.pyplot(fig)
    st.bar_chart

    drop_temp_table()

# Function for Question 4: Get the Top 5 Most Expensive Books by Retail Price
def top_5_expensive_books(data_list):
    create_temp_table(data_list)
    query = """
        SELECT book_title, amount_retailPrice
        FROM temp_books
        WHERE amount_retailPrice IS NOT NULL
        ORDER BY amount_retailPrice DESC
        LIMIT 5;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["Book Title", "Retail Price"])
    df.index = df.index + 1
    st.dataframe(df)

    fig, ax = plt.subplots()
    bars = ax.bar(df["Book Title"], df["Retail Price"], color=['violet', 'white'])  
    ax.set_facecolor('lightgray')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height, height, ha='center', va='bottom')

    ax.set_title("Top 5 Most Expensive Books", color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.1'))  
    ax.set_xlabel("Book Title", color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2')) 
    ax.set_ylabel("Retail Price", color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))  
    ax.set_xticks(range(len(df["Book Title"])))  
    ax.set_xticklabels(df["Book Title"].tolist(), rotation=90)  
    ax.title.set_position([0.5, 1.1])
    plt.subplots_adjust(top=0.9)
    st.pyplot(fig)
    

    drop_temp_table()

# Function for Question 5: Find Books Published After 2010 with at Least 500 Pages
def books_after_2010_500_pages(data_list):
    create_temp_table(data_list)
    query = """
        SELECT book_title, year, pageCount
        FROM temp_books
        WHERE CAST(year AS UNSIGNED) > 2010 AND pageCount >= 500
        ORDER BY year,pageCount DESC;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["Book Title", "Year", "Page Count"])
    df.index = df.index + 1
    st.dataframe(df)

    fig, ax = plt.subplots()
    ax.scatter(df["Year"], df["Page Count"], color='orange') 
    ax.set_facecolor('lightgray')
    ax.grid(axis='both', linestyle='--', alpha=0.7) 
    
        
    ax.set_title("Books Published After 2010 with at Least 500 Pages", color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.1')) 
    ax.set_xlabel("Year", color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2')) 
    ax.set_ylabel("Page Count", color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2')) 
    
    ax.set_xticks(df["Year"].unique()) 
    ax.set_xticklabels(df["Year"].unique(), rotation=45, ha='right') 
    
    ax.title.set_position([0.5, 1.1])
    plt.subplots_adjust(top=0.9)
    st.pyplot(fig)

    drop_temp_table()

# Function for Question 6: List Books with Discounts Greater than 20%
def books_with_discounts(data_list):
    create_temp_table(data_list)
    query = """
        SELECT book_title, amount_listPrice, amount_retailPrice,
                (amount_listPrice - amount_retailPrice) / amount_listPrice * 100 AS discount_percentage
        FROM temp_books
        WHERE amount_listPrice > 0 AND amount_retailPrice > 0
        AND (amount_listPrice - amount_retailPrice) / amount_listPrice > 0.20
        ORDER BY discount_percentage DESC;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["Book Title", "List Price", "Retail Price", "Discount Percentage"])
    df.index = df.index + 1
    st.dataframe(df)

    fig, ax = plt.subplots()
    bars = ax.bar(df["Book Title"], df["Discount Percentage"], color=['violet', 'white','cyan'])  
    ax.set_facecolor('lightgray')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.1f}%', ha='center', va='bottom',fontsize=2) 

    ax.set_title("Books with Discounts Greater than 20%", color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.1')) 
    ax.set_xlabel("Book Title", color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))  
    ax.set_ylabel("Discount Percentage", color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2')) 
    ax.set_xticks(range(len(df["Book Title"])))  
    ax.set_xticklabels(df["Book Title"].tolist(), rotation=90)  
    ax.title.set_position([0.5, 1.1])
    plt.subplots_adjust(top=0.9)
    st.pyplot(fig)

    drop_temp_table()

# Function for Question 7: Find the Average Page Count for eBooks vs Physical Books
def avg_page_count_ebook_physical(data_list):
    create_temp_table(data_list)
    query = """
        SELECT isEbook, AVG(pageCount) AS avg_page_count
        FROM temp_books
        GROUP BY isEbook;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["isEbook", "Average Page Count"])
    df.index = df.index + 1
    st.dataframe(df)

    fig, ax = plt.subplots()
    bars = ax.bar(df["isEbook"], df["Average Page Count"], color=['blue', 'lightcoral']) 
    ax.set_facecolor('lightgray')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.2f}', ha='center', va='bottom') 

    ax.set_title("Average Page Count for eBooks vs Physical Books", color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.1'))  
    ax.set_xlabel("Book Format (eBook: 1, Physical: 0)", color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))  
    ax.set_ylabel("Average Page Count", color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))
    ax.set_xticks(df["isEbook"])  
    ax.set_xticklabels(["Physical Book", "eBook"]) 
    ax.title.set_position([0.5, 1.1])
    plt.subplots_adjust(top=0.9)
    st.pyplot(fig)

    drop_temp_table()

# Function for Question 8: Find the Top 3 Authors with the Most Books
def top_3_authors(data_list):
    create_temp_table(data_list)
    query = """
        SELECT book_authors, COUNT(*) AS book_count
        FROM temp_books
        GROUP BY book_authors
        ORDER BY book_count DESC
        LIMIT 4;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["Author", "Book Count"])
    df.index = df.index + 1

    if df.loc[1, "Author"] == "No authors available":
        st.dataframe(df)
    elif df.loc[2, "Author"] == "No authors available":
        st.dataframe(pd.concat([df.iloc[[1]], df.iloc[[3,4]]]))
    elif df.loc[3, "Author"] == "No authors available":
        st.dataframe(df.iloc[[1,2,4]])
    else:
        st.dataframe(df.head(4))

    fig, ax = plt.subplots()
    bars = ax.bar(df["Author"], df["Book Count"], color=['maroon', 'coral', 'green']) 
    ax.set_facecolor('lightgray')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height, height, ha='center', va='bottom')  

    ax.set_title("Top 3 Authors with the Most Books", color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.1')) 
    ax.set_xlabel("Author", color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))  
    ax.set_ylabel("Book Count", color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))  
    ax.set_xticks(range(len(df["Author"])))  
    ax.set_xticklabels(df["Author"].tolist(), rotation=90)  
    ax.title.set_position([0.5, 1.1])
    plt.subplots_adjust(top=0.9)
    st.pyplot(fig)

    drop_temp_table()

# Function for Question 9: List Publishers with More than 10 Books
def publishers_more_than_10_books(data_list):
    create_temp_table(data_list)
    query = """
    SELECT publisher, COUNT(*) AS book_count
    FROM temp_books
    GROUP BY publisher
    HAVING COUNT(*) > 10
    ORDER BY book_count DESC, publisher;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["Publisher", "Book Count"])
    df.index = df.index + 1
    st.dataframe(df)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(df["Publisher"], df["Book Count"], color=['pink', 'lavender'])
    ax.set_facecolor('lightgray')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    ax.bar_label(bars)    
        
    ax.set_title("Publishers with More than 10 Books", color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.1'))
    ax.set_xlabel("Publisher", color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))
    ax.set_ylabel("Book Count", color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))
    ax.set_xticks(range(len(df["Publisher"])))
    ax.set_xticklabels(df["Publisher"].tolist(), ha='center') 
    ax.title.set_position([0.5, 1.1])
    plt.subplots_adjust(top=0.9)
    st.pyplot(fig)

    drop_temp_table()

# Function for Question 10: Find the Average Page Count for Each Category
def avg_page_count_per_category(data_list):
    create_temp_table(data_list)
    query = """
        SELECT categories, AVG(pageCount) AS avg_page_count
        FROM temp_books
        GROUP BY categories
        ORDER BY avg_page_count DESC, categories;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["Category", "Average Page Count"])
    df.index = df.index + 1
    st.dataframe(df)

    st.bar_chart(df.set_index("Category")["Average Page Count"])

    drop_temp_table()

# Function for Question 11: Retrieve Books with More than 3 Authors
def books_with_more_than_3_authors(data_list):
    create_temp_table(data_list)
    query = """
        SELECT book_title, book_authors
        FROM temp_books
        WHERE LENGTH(book_authors) - LENGTH(REPLACE(book_authors, ',', '')) >= 2;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["Book Title", "Authors"])
    df.index = df.index + 1
    st.dataframe(df)

    fig, ax = plt.subplots(figsize=(10, 6)) 
    author_counts = [len(authors.split(',')) for authors in df["Authors"]]  
    bars = ax.bar(df["Authors"], author_counts, color=['white', 'pink','cyan']) 
    ax.set_facecolor('lightgray')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    ax.bar_label(bars)  

    ax.set_title("Books with More than 3 Authors", color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.1'))
    ax.set_xlabel("Author", color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))
    ax.set_ylabel("Number of Authors", color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))
    ax.set_xticks(range(len(df["Authors"])))
    ax.set_xticklabels(df["Authors"].tolist(), rotation=90) 
    ax.title.set_position([0.5, 1.1])
    plt.subplots_adjust(top=0.9)
    st.pyplot(fig)

    drop_temp_table()

# Function for Question 12: Books with Ratings Count Greater Than the Average
def books_ratings_greater_than_avg(data_list):
    create_temp_table(data_list)
    cursor.execute("SELECT AVG(averageRating) FROM temp_books")
    avg_rating = cursor.fetchone()[0] 

    query = f"""
    SELECT book_title, averageRating
    FROM temp_books
    WHERE averageRating > {avg_rating}
    """

    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["Book Title", "Ratings Count"])
    df.index = df.index + 1
    st.dataframe(df)

    st.bar_chart(df.set_index("Book Title")["Ratings Count"])
    
    drop_temp_table()

# Function for Question 13: Books with the Same Author Published in the Same Year
def books_same_author_same_year(data_list):
    create_temp_table(data_list)
    query = """
        SELECT  GROUP_CONCAT(book_title) AS book_titles, book_authors, year
        FROM temp_books
        GROUP BY book_authors, year
        HAVING COUNT(*) > 1
        ORDER BY book_authors, year DESC;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["Book Title", "Author", "Year"])
    df.index = df.index + 1
    st.dataframe(df)

    fig, ax = plt.subplots(figsize=(10, 6))

    author_year_counts = df.groupby(["Author", "Year"])['Book Title'].agg(lambda x: ','.join(x)).reset_index()
    author_year_counts.rename(columns={'Book Title': 'Book Titles'}, inplace=True)
    author_year_counts['Book Count'] = author_year_counts['Book Titles'].str.split(',').apply(len)

    no_author_data = author_year_counts[author_year_counts["Author"] == "No authors available"]
    other_author_data = author_year_counts[author_year_counts["Author"] != "No authors available"]

    no_author_data_grouped = no_author_data.groupby("Year")['Book Titles'].agg(lambda x: ','.join(x)).reset_index()
    no_author_data_grouped['Book Count'] = no_author_data_grouped['Book Titles'].str.split(',').apply(len)
    
    st.title("Authors Available")
    st.bar_chart(other_author_data.set_index("Author")["Book Count"]) 
    st.title("Authors Unavailable")
    st.bar_chart(no_author_data_grouped.set_index("Year")["Book Count"]) 

    drop_temp_table()

# Function for Question 14: Books with a Specific Keyword in the Title
def books_with_keyword_in_title(data_list, keyword):
  create_temp_table(data_list)
  query = f"""
      SELECT book_title
      FROM temp_books
      WHERE LOWER(book_title) LIKE LOWER('%{keyword}%');
  """
  cursor.execute(query)
  data = cursor.fetchall()
  df = pd.DataFrame(data, columns=["Book Title"])
  df.index = df.index + 1

  if df.empty:
    st.info("No results found for the keyword: ", keyword)
  else:
    st.dataframe(df) 

  drop_temp_table()

# Function for Question 15: Year with the Highest Average Book Price
def year_highest_avg_price(data_list):
    create_temp_table(data_list)
    query = """
        SELECT year, AVG(amount_retailPrice) AS avg_price
        FROM temp_books
        GROUP BY year
        ORDER BY avg_price DESC
        LIMIT 1;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["Year", "Average Price"])
    df.index = df.index + 1
    st.dataframe(df)

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.bar(df["Year"], df["Average Price"], color=['blue']) 
    ax.bar_label(bars, labels=[f'{val:.2f}' for val in df["Average Price"]], padding=3, fontsize=8) 

    ax.set_title("Year with the Highest Average Book Price", color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.1'))
    ax.set_xlabel("Year", color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))
    ax.set_ylabel("Average Price", color='white', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))
    ax.set_facecolor('lightgray')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    st.pyplot(fig)  

    drop_temp_table()

# Function for Question 16: Count Authors Who Published 3 Consecutive Years
def authors_published_3_consecutive_years(data_list):
    create_temp_table(data_list)
    query = """
        SELECT book_authors, COUNT(DISTINCT year) AS num_years
        FROM temp_books
        GROUP BY book_authors
        HAVING COUNT(DISTINCT year) >= 3
        ORDER BY num_years DESC,book_authors;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['book_authors', 'num_years'])
    df.index = df.index + 1
    st.dataframe(df)

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.bar(df['book_authors'], df['num_years'], color=['blue'])  
    ax.bar_label(bars, padding=3, fontsize=8)

    ax.set_title("Authors Who Published for 3 or More Consecutive Years", color='white',
                 bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.1'))
    ax.set_xlabel("Authors", color='white',
                 bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))
    ax.set_ylabel("Number of Years", color='white',
                 bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))
    ax.set_facecolor('lightgray')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)

    drop_temp_table()

# Function for Question 17: Find authors who published books in the same year but under different publishers
def authors_same_year_diff_publishers(data_list):
    create_temp_table(data_list)
    query = """
        SELECT book_authors, year, COUNT(*) AS num_books, GROUP_CONCAT(DISTINCT publisher) AS publishers
        FROM temp_books
        GROUP BY book_authors, year
        HAVING COUNT(DISTINCT publisher) > 1
        ORDER BY book_authors, year DESC;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["Author", "Year", "Book Count", "Publisher"])
    df.index = df.index + 1
    if df.empty:
        st.write("No authors available who published books in the same year but under different publishers")
    else:
        st.dataframe(df)

        fig, ax = plt.subplots(figsize=(10, 6))

        bars = ax.bar(df['Author'], df['Book Count'], color = ['brown','black','white','maroon']) 
        ax.bar_label(bars, padding=3, fontsize=8)  

        ax.set_title("Authors Who Published Books in the Same Year with Different Publishers", color='white',
                    bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.1'))
        ax.set_xlabel("Author", color='white',
                    bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))
        ax.set_ylabel("Book Count", color='white',
                    bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))
        ax.set_facecolor('lightgray')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        plt.xticks(rotation=90)  

        st.pyplot(fig)


    drop_temp_table()

# Function for Question 18: Find the average amount_retailPrice of eBooks and physical books
def avg_price_ebook_physical(data_list):
    create_temp_table(data_list)
    query = """
        SELECT
            AVG(CASE WHEN isEbook = 1 THEN amount_retailPrice ELSE NULL END) AS avg_ebook_price,
            AVG(CASE WHEN isEbook = 0 THEN amount_retailPrice ELSE NULL END) AS avg_physical_price
        FROM temp_books;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["Average eBook Price", "Average Physical Price"])
    df.index = df.index + 1
    st.dataframe(df)

    fig, ax = plt.subplots(figsize=(8, 6))

    values = df.iloc[0].fillna(0).values

    bars = ax.bar(["eBook", "Physical"], values, color = ['black','white'])  
    ax.bar_label(bars, labels=[f'{val:.2f}' for val in values], padding=3, fontsize=8) 

    ax.set_title("Average Price of eBooks vs Physical Books", color='white',
                 bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.1'))
    ax.set_ylabel("Average Price", color='white',
                 bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))
    ax.set_facecolor('lightgray')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    st.pyplot(fig)

    drop_temp_table()

# Function for Question 19: Identify books that have an averageRating that is more than two standard deviations away from the average rating of all books
def outlier_books_by_rating(data_list):
    create_temp_table(data_list)
    cursor.execute("SELECT AVG(averageRating) FROM temp_books")
    avg_rating = cursor.fetchone()[0]

    cursor.execute("SELECT STDDEV(averageRating) FROM temp_books")
    std_rating = cursor.fetchone()[0]

    query = f"""
        SELECT book_title, averageRating, ratingsCount
        FROM temp_books
        WHERE averageRating > {avg_rating} + 2 * {std_rating}
        OR averageRating < {avg_rating} - 2 * {std_rating}
        ORDER BY averageRating DESC,ratingsCount DESC;
    """

    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["Book Title", "Average Rating", "Ratings Count"])
    df.index = df.index + 1
    st.dataframe(df)

    st.scatter_chart(df.set_index("Average Rating")[["Ratings Count"]])

    drop_temp_table()

# Function for Question 20: Find the publisher with the highest average rating, having published more than 10 books.
def publisher_highest_avg_rating(data_list):
    create_temp_table(data_list)
    query = """
        SELECT publisher, AVG(averageRating) AS avg_rating, COUNT(*) as num_books
        FROM temp_books
        GROUP BY publisher
        HAVING COUNT(*) > 10
        ORDER BY avg_rating DESC
        LIMIT 1;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["Publisher", "Average Rating", "Number of Books"])
    df.index = df.index + 1
    if not df.empty:
        st.dataframe(df)
        publisher = df.loc[1, "Publisher"]
        avg_rating = df.loc[1, "Average Rating"]
        num_books = df.loc[1, "Number of Books"]
        st.write(f"The publisher with the highest average rating and more than 10 books is:  {publisher}")
        st.write(f"Average Rating:  {avg_rating:.2f}")
        st.write(f"Number of Books Published:  {num_books}")

        fig, ax = plt.subplots(figsize=(8, 6))

        bars = ax.bar(df["Publisher"], df["Average Rating"], color =['pink'])
        ax.bar_label(bars, labels=[f'{val:.2f}' for val in df["Average Rating"]], padding=3, fontsize=8)  

        ax.set_title("Publisher with Highest Average Rating (More than 10 Books)", color='white',
                     bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.1'))
        ax.set_xlabel("Publisher", color='white',
                     bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))
        ax.set_ylabel("Average Rating", color='white',
                     bbox=dict(facecolor='black', edgecolor='black', boxstyle='round,pad=0.2'))
        ax.set_facecolor('lightgray')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        st.pyplot(fig)
    else:
        st.write("No publisher found with more than 10 books and a calculated average rating.")        

    drop_temp_table()


# Main Database insertion to insert all the values in one table  
def myDatabase_insertion(data_list):
  try:
      cursor.execute("""CREATE TABLE IF NOT EXISTS google_books (
        S_no INT AUTO_INCREMENT UNIQUE,
        book_id VARCHAR(255) PRIMARY KEY,
        search_key VARCHAR(255),
        book_title VARCHAR(500),
        book_subtitle TEXT,
        book_authors TEXT,
        book_description TEXT,
        industryIdentifiers TEXT,
        text_readingModes BOOLEAN,
        image_readingModes BOOLEAN,
        pageCount INT,
        categories TEXT,
        language VARCHAR(50),
        imageLinks TEXT,
        ratingsCount INT,
        averageRating FLOAT,
        country VARCHAR(50),
        saleability VARCHAR(50),
        isEbook BOOLEAN,
        amount_listPrice FLOAT,
        currencyCode_listPrice VARCHAR(10),
        amount_retailPrice FLOAT,
        currencyCode_retailPrice VARCHAR(10),
        buyLink TEXT,
        year VARCHAR(4),
        publisher TEXT);"""
        )

      insert_query = """INSERT IGNORE INTO google_books (book_id, search_key, book_title, book_subtitle, book_authors, book_description,
                        industryIdentifiers, text_readingModes, image_readingModes, pageCount, categories,
                        language, imageLinks, ratingsCount, averageRating, country, saleability, isEbook,
                        amount_listPrice, currencyCode_listPrice, amount_retailPrice, currencyCode_retailPrice, buyLink, year, publisher)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
      insert_values = [tuple(d.values()) for d in data_list]
      cursor.executemany(insert_query, insert_values)
      mydb.commit()
  except pymysql.Error as err:
        st.error(f"Database error: {err}")

# Fetch books from Google API
def fetch_and_store_books(search_query , api_key , max_results):
    if not  search_query:
        raise ValueError("Search query cannot be empty")
    if not 1 <= max_results <= 1000:
        raise ValueError("no. of datas to be retrieved must be between 1 and 1000")
    data_list = []
    startIndex = 0
    total_items_fetched = 0
    unique_book_ids = set()  

    while total_items_fetched < max_results:
        url = f"https://www.googleapis.com/books/v1/volumes?q={search_query}&startIndex={startIndex}&maxResults=40&key={api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()  
            data = response.json()
        except requests.exceptions.RequestException as e:
            if isinstance(e, requests.exceptions.HTTPError) and e.response:
                status_code = e.response.status_code
                st.error(f"An error occurred during the API request: {e} (Status code: {status_code})")
            else:
                st.error(f"An error occurred during the API request: {e}")
            

        items = data.get('items', [])

        for item in items:
          if total_items_fetched >= max_results:
            break

          volume_info = item.get('volumeInfo', {})
          sale_info = item.get('saleInfo', {})
          search_info = item.get('searchInfo', {})

          book_id = item.get('id') 
          if book_id and book_id not in unique_book_ids:
              search_key = search_query
              book_title = volume_info.get('title','No title mentioned')
              book_subtitle = volume_info.get('subtitle', 'No subtitle available')
              book_authors = ', '.join(volume_info.get('authors', []))
              if not book_authors or book_authors.strip(', ') == '':
                book_authors = 'No authors available'
              book_description = volume_info.get('description','No description available')
              industryIdentifiers = volume_info.get('industryIdentifiers','No industryIdentifiers available')
              if industryIdentifiers:
                  industryIdentifiers = json.dumps(industryIdentifiers)
              else:
                  industryIdentifiers = None
              text_readingModes = volume_info.get('readingModes', {}).get('text')
              image_readingModes = volume_info.get('readingModes', {}).get('image')
              pageCount = volume_info.get('pageCount',0)
              categories = ', '.join(volume_info.get('categories', 'Not applicable'))
              language = volume_info.get('language','No language mentioned')
              imageLinks = volume_info.get('imageLinks','No image link has been attached')
              if isinstance(imageLinks, dict):
                imageLinks = json.dumps(imageLinks)
              ratingsCount = volume_info.get('ratingsCount',0)
              averageRating = volume_info.get('averageRating',0)
              country = sale_info.get('country','No country is mentioned')
              saleability = sale_info.get('saleability')
              isEbook = sale_info.get('isEbook')
              amount_listPrice = sale_info.get('listPrice', {}).get('amount')
              currencyCode_listPrice = sale_info.get('listPrice', {}).get('currencyCode')
              amount_retailPrice = sale_info.get('retailPrice', {}).get('amount')
              currencyCode_retailPrice = sale_info.get('retailPrice', {}).get('currencyCode')
              buyLink = sale_info.get('buyLink','Link is not available')
              year = volume_info.get('publishedDate', '')[:4]
              publisher = volume_info.get('publisher', 'Unknown Publisher')

              data_dic= {
                  'book_id': book_id,
                  'search_key': search_key,
                  'book_title': book_title,
                  'book_subtitle': book_subtitle,
                  'book_authors':book_authors ,
                  'book_description': book_description,
                  'industryIdentifiers': industryIdentifiers,
                  'text_readingModes': text_readingModes,
                  'image_readingModes': image_readingModes,
                  'pageCount': pageCount,
                  'categories': categories,
                  'language': language,
                  'imageLinks': imageLinks,
                  'ratingsCount': ratingsCount,
                  'averageRating': averageRating,
                  'country': country,
                  'saleability': saleability,
                  'isEbook': isEbook,
                  'amount_listPrice': amount_listPrice,
                  'currencyCode_listPrice': currencyCode_listPrice,
                  'amount_retailPrice': amount_retailPrice,
                  'currencyCode_retailPrice': currencyCode_retailPrice,
                  'buyLink': buyLink,
                  'year': year,
                  'publisher': publisher
              }

              data_list.append(data_dic)
              unique_book_ids.add(book_id)
              total_items_fetched += 1

        startIndex += 40


        if not items:  
          break

    myDatabase_insertion(data_list)

    return data_list

#streamlit page code
st.set_page_config(page_title="Book Scape Explorer", page_icon=":books:", layout="centered")

selected_tab = st.sidebar.radio("Navigation", ["Fetch Books", "Data Analytic Insights"])
# Fetch Books tab
if selected_tab == "Fetch Books":
    st.title("Fetch Books from Google Books API")
    search_query = st.text_input("Enter search query:")
    max_results = st.number_input("Enter number of results to retrieve (1-1000):", min_value=1, max_value=1000, value=100)

    if st.button("Submit"):
        if search_query and max_results:
            try:

                fetch_and_store_books(search_query, api_key, max_results)

                st.write("Fetching and storing books...")
                data_list = fetch_and_store_books(search_query, api_key, max_results) 
                df = pd.DataFrame(data_list)
                df.index = df.index+1
                st.session_state.book_data = data_list
                st.dataframe(df)
                st.write("Books fetched and stored successfully!")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please fill in both search query and number of results.")

# Data visualization tab
elif selected_tab == "Data Analytic Insights":
    st.title("Data Analytic Insights")

    if 'book_data'  in st.session_state:
        data_list = st.session_state.book_data 
        analysis_options = [
            "Check Availability of eBooks vs Physical Books",
            "Find the Publisher with the Most Books Published",
            "Identify the Publisher with the Highest Average Rating",
            "Get the Top 5 Most Expensive Books by Retail Price",
            "Find Books Published After 2010 with at Least 500 Pages",
            "List Books with Discounts Greater than 20%",
            "Find the Average Page Count for eBooks vs Physical Books",
            "Find the Top 3 Authors with the Most Books",
            "List Publishers with More than 10 Books",
            "Find the Average Page Count for Each Category",
            "Retrieve Books with More than 3 Authors",
            "Books with Ratings Count Greater Than the Average",
            "Books with the Same Author Published in the Same Year",
            "Books with a Specific Keyword in the Title",
            "Year with the Highest Average Book Price",
            "Count Authors Who Published 3 Consecutive Years",
            "Find authors who published books in the same year but under different publishers",
            "Find the average amount_retailPrice of eBooks and physical books",
            "Identify books that have an averageRating that is more than two standard deviations away from the average rating of all books",
            "Find the publisher with the highest average rating, having published more than 10 books"
        ]

        selected_analysis = st.selectbox("Select analysis:", analysis_options)

        if selected_analysis == "Check Availability of eBooks vs Physical Books":
            check_ebook_availability(data_list)
        elif selected_analysis == "Find the Publisher with the Most Books Published":
            publisher_most_books(data_list)
        elif selected_analysis == "Identify the Publisher with the Highest Average Rating":
            publisher_highest_avg_rating_overall(data_list)
        elif selected_analysis == "Get the Top 5 Most Expensive Books by Retail Price":
            top_5_expensive_books(data_list)
        elif selected_analysis == "Find Books Published After 2010 with at Least 500 Pages":
            books_after_2010_500_pages(data_list)
        elif selected_analysis == "List Books with Discounts Greater than 20%":
            books_with_discounts(data_list)
        elif selected_analysis == "Find the Average Page Count for eBooks vs Physical Books":
            avg_page_count_ebook_physical(data_list)
        elif selected_analysis == "Find the Top 3 Authors with the Most Books":
            top_3_authors(data_list)
        elif selected_analysis == "List Publishers with More than 10 Books":
            publishers_more_than_10_books(data_list)
        elif selected_analysis == "Find the Average Page Count for Each Category":
            avg_page_count_per_category(data_list)
        elif selected_analysis == "Retrieve Books with More than 3 Authors":
            books_with_more_than_3_authors(data_list)
        elif selected_analysis == "Books with Ratings Count Greater Than the Average":
            books_ratings_greater_than_avg(data_list)
        elif selected_analysis == "Books with the Same Author Published in the Same Year":
            books_same_author_same_year(data_list)
        elif selected_analysis == "Books with a Specific Keyword in the Title":
            keyword = st.text_input("Enter keyword:")
            if keyword:
                books_with_keyword_in_title(data_list, keyword)
            else:
                st.warning("Please enter a keyword.")
        elif selected_analysis == "Year with the Highest Average Book Price":
            year_highest_avg_price(data_list)
        elif selected_analysis == "Count Authors Who Published 3 Consecutive Years":
            authors_published_3_consecutive_years(data_list)
        elif selected_analysis == "Find authors who published books in the same year but under different publishers":
            authors_same_year_diff_publishers(data_list)
        elif selected_analysis == "Find the average amount_retailPrice of eBooks and physical books":
            avg_price_ebook_physical(data_list)
        elif selected_analysis == "Identify books that have an averageRating that is more than two standard deviations away from the average rating of all books":
            outlier_books_by_rating(data_list)
        elif selected_analysis == "Find the publisher with the highest average rating, having published more than 10 books":
            publisher_highest_avg_rating(data_list)
    else:
        st.warning("Please fetch books first to generate insights.")

cursor.close()
mydb.close()
