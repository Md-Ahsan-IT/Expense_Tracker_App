import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
import csv
import os

# Page configuration
st.set_page_config(
    page_title="Daily Expense Tracker",
    page_icon="💰",
    layout="wide"
)

# Initialize session state
if 'expenses' not in st.session_state:
    st.session_state.expenses = []
if 'categories' not in st.session_state:
    st.session_state.categories = [
        'Food', 'Transportation', 'Entertainment', 'Utilities',
        'Healthcare', 'Shopping', 'Education', 'Other'
    ]

def load_data():
    """Load expenses from JSON file"""
    try:
        if os.path.exists('expenses.json'):
            with open('expenses.json', 'r') as file:
                st.session_state.expenses = json.load(file)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.session_state.expenses = []

def save_data():
    """Save expenses to JSON file"""
    try:
        with open('expenses.json', 'w') as file:
            json.dump(st.session_state.expenses, file, indent=2)
    except Exception as e:
        st.error(f"Error saving data: {e}")

# Load data when app starts
load_data()

# Main app
st.title("💰 Daily Expense Tracker")
st.markdown("---")

# Sidebar for navigation
menu = st.sidebar.selectbox(
    "Navigation",
    ["🏠 Dashboard", "➕ Add Expense", "📊 View Expenses", "📈 Monthly Reports", "🔍 Search", "⚙️ Statistics"]
)

# Dashboard
if menu == "🏠 Dashboard":
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_expenses = sum(exp['amount'] for exp in st.session_state.expenses)
        st.metric("Total Expenses", f"₹{total_expenses:,.2f}")
    
    with col2:
        st.metric("Total Records", len(st.session_state.expenses))
    
    with col3:
        if st.session_state.expenses:
            avg_expense = total_expenses / len(st.session_state.expenses)
            st.metric("Average Expense", f"₹{avg_expense:.2f}")
        else:
            st.metric("Average Expense", "₹0.00")
    
    # Recent expenses
    st.subheader("Recent Expenses")
    if st.session_state.expenses:
        recent_expenses = st.session_state.expenses[-5:][::-1]  # Last 5 expenses
        for exp in recent_expenses:
            with st.container():
                col1, col2, col3 = st.columns([2,1,1])
                with col1:
                    st.write(f"**{exp['description']}**")
                with col2:
                    st.write(f"₹{exp['amount']:.2f}")
                with col3:
                    st.write(f"_{exp['category']}_")
                st.write(f"Date: {exp['date']}")
                st.divider()
    else:
        st.info("No expenses recorded yet. Add your first expense!")

# Add Expense
elif menu == "➕ Add Expense":
    st.subheader("Add New Expense")
    
    with st.form("add_expense_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input("Date", datetime.now())
            amount = st.number_input("Amount (₹)", min_value=0.0, step=1.0)
        
        with col2:
            category = st.selectbox("Category", st.session_state.categories)
            description = st.text_input("Description")
        
        submitted = st.form_submit_button("💾 Save Expense")
        
        if submitted:
            if amount > 0 and description.strip():
                expense = {
                    'id': len(st.session_state.expenses) + 1,
                    'date': date.strftime("%Y-%m-%d"),
                    'amount': amount,
                    'category': category,
                    'description': description
                }
                st.session_state.expenses.append(expense)
                save_data()
                st.success("✅ Expense added successfully!")
            else:
                st.error("Please enter valid amount and description")

# View Expenses
elif menu == "📊 View Expenses":
    st.subheader("View Expenses")
    
    if st.session_state.expenses:
        # Convert to DataFrame for better display
        df = pd.DataFrame(st.session_state.expenses)
        df['amount'] = df['amount'].apply(lambda x: f"₹{x:.2f}")
        
        st.dataframe(
            df[['date', 'amount', 'category', 'description']],
            use_container_width=True,
            hide_index=True
        )
        
        # Export option
        if st.button("📥 Export to CSV"):
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="all_expenses.csv",
                mime="text/csv"
            )
    else:
        st.info("No expenses to display")

# Monthly Reports
elif menu == "📈 Monthly Reports":
    st.subheader("Monthly Expense Report")
    
    if st.session_state.expenses:
        # Year-month selection
        col1, col2 = st.columns(2)
        with col1:
            years = sorted(set(exp['date'][:4] for exp in st.session_state.expenses), reverse=True)
            selected_year = st.selectbox("Select Year", years)
        
        with col2:
            months = list(range(1, 13))
            month_names = ["January", "February", "March", "April", "May", "June",
                          "July", "August", "September", "October", "November", "December"]
            selected_month = st.selectbox("Select Month", months, format_func=lambda x: month_names[x-1])
        
        # Filter expenses for selected month
        monthly_expenses = [
            exp for exp in st.session_state.expenses 
            if exp['date'].startswith(f"{selected_year}-{selected_month:02d}")
        ]
        
        if monthly_expenses:
            total_amount = sum(exp['amount'] for exp in monthly_expenses)
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Spent", f"₹{total_amount:,.2f}")
            with col2:
                st.metric("Transactions", len(monthly_expenses))
            with col3:
                avg_daily = total_amount / len(set(exp['date'] for exp in monthly_expenses))
                st.metric("Avg Daily", f"₹{avg_daily:.2f}")
            
            # Category breakdown
            st.subheader("Category Breakdown")
            category_totals = {}
            for exp in monthly_expenses:
                category_totals[exp['category']] = category_totals.get(exp['category'], 0) + exp['amount']
            
            # Display as columns
            cols = st.columns(len(category_totals))
            for idx, (category, amount) in enumerate(category_totals.items()):
                with cols[idx % len(cols)]:
                    percentage = (amount / total_amount) * 100
                    st.metric(category, f"₹{amount:.2f}", f"{percentage:.1f}%")
            
            # Daily trend chart
            st.subheader("Daily Spending Trend")
            daily_data = {}
            for exp in monthly_expenses:
                daily_data[exp['date']] = daily_data.get(exp['date'], 0) + exp['amount']
            
            chart_df = pd.DataFrame(list(daily_data.items()), columns=['Date', 'Amount'])
            chart_df = chart_df.sort_values('Date')
            st.line_chart(chart_df.set_index('Date'))
            
        else:
            st.warning(f"No expenses found for {month_names[selected_month-1]} {selected_year}")
    else:
        st.info("No expenses recorded yet")

# Search Expenses
elif menu == "🔍 Search":
    st.subheader("Search Expenses")
    
    if st.session_state.expenses:
        search_type = st.radio("Search by:", ["Description", "Category", "Date Range", "Amount Range"])
        
        if search_type == "Description":
            search_term = st.text_input("Enter search term")
            if search_term:
                results = [exp for exp in st.session_state.expenses 
                          if search_term.lower() in exp['description'].lower()]
                if results:
                    st.write(f"Found {len(results)} matching expenses:")
                    for exp in results:
                        st.write(f"**{exp['date']}** - ₹{exp['amount']:.2f} - {exp['category']} - {exp['description']}")
                else:
                    st.info("No matching expenses found")
        
        elif search_type == "Category":
            selected_category = st.selectbox("Select Category", st.session_state.categories)
            results = [exp for exp in st.session_state.expenses if exp['category'] == selected_category]
            if results:
                total = sum(exp['amount'] for exp in results)
                st.write(f"**{selected_category}**: {len(results)} expenses, Total: ₹{total:.2f}")
                for exp in results:
                    st.write(f"**{exp['date']}** - ₹{exp['amount']:.2f} - {exp['description']}")
        
        elif search_type == "Date Range":
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date")
            with col2:
                end_date = st.date_input("End Date")
            
            if start_date and end_date:
                results = [exp for exp in st.session_state.expenses 
                          if start_date.strftime("%Y-%m-%d") <= exp['date'] <= end_date.strftime("%Y-%m-%d")]
                if results:
                    total = sum(exp['amount'] for exp in results)
                    st.write(f"Found {len(results)} expenses, Total: ₹{total:.2f}")
                    for exp in results:
                        st.write(f"**{exp['date']}** - ₹{exp['amount']:.2f} - {exp['category']} - {exp['description']}")
        
        elif search_type == "Amount Range":
            col1, col2 = st.columns(2)
            with col1:
                min_amount = st.number_input("Minimum Amount", min_value=0.0, value=0.0)
            with col2:
                max_amount = st.number_input("Maximum Amount", min_value=0.0, value=1000.0)
            
            results = [exp for exp in st.session_state.expenses 
                      if min_amount <= exp['amount'] <= max_amount]
            if results:
                total = sum(exp['amount'] for exp in results)
                st.write(f"Found {len(results)} expenses, Total: ₹{total:.2f}")
                for exp in results:
                    st.write(f"**{exp['date']}** - ₹{exp['amount']:.2f} - {exp['category']} - {exp['description']}")
    else:
        st.info("No expenses to search")

# Statistics
elif menu == "⚙️ Statistics":
    st.subheader("Expense Statistics")
    
    if st.session_state.expenses:
        total_amount = sum(exp['amount'] for exp in st.session_state.expenses)
        avg_amount = total_amount / len(st.session_state.expenses)
        
        # Most expensive
        most_expensive = max(st.session_state.expenses, key=lambda x: x['amount'])
        
        # Category statistics
        category_stats = {}
        for exp in st.session_state.expenses:
            category_stats[exp['category']] = category_stats.get(exp['category'], 0) + exp['amount']
        
        # Display stats
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Spending", f"₹{total_amount:,.2f}")
            st.metric("Average per Expense", f"₹{avg_amount:.2f}")
            st.metric("Total Records", len(st.session_state.expenses))
        
        with col2:
            st.metric("Most Expensive", f"₹{most_expensive['amount']:.2f}")
            st.write(f"**{most_expensive['category']}** - {most_expensive['description']}")
            st.write(f"Date: {most_expensive['date']}")
        
        # Category chart
        st.subheader("Spending by Category")
        if category_stats:
            chart_data = pd.DataFrame(list(category_stats.items()), columns=['Category', 'Amount'])
            st.bar_chart(chart_data.set_index('Category'))
    
    else:
        st.info("No expenses recorded yet")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip**: Your data is automatically saved to 'expenses.json' file")