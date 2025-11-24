import json
import os
from datetime import datetime, timedelta
import csv

class ExpenseTracker:
    def __init__(self, data_file='expenses.json'):
        self.data_file = data_file
        self.expenses = []
        self.categories = [
            'Food', 'Transportation', 'Entertainment', 'Utilities', 
            'Healthcare', 'Shopping', 'Education', 'Other'
        ]
        self.load_data()
    
    def load_data(self):
        """Load expenses from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as file:
                    self.expenses = json.load(file)
                print(f"Loaded {len(self.expenses)} existing expense records.")
            else:
                self.expenses = []
                print("No existing data found. Starting fresh.")
        except Exception as e:
            print(f"Error loading data: {e}")
            self.expenses = []
    
    def save_data(self):
        """Save expenses to JSON file"""
        try:
            with open(self.data_file, 'w') as file:
                json.dump(self.expenses, file, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def add_expense(self):
        """Add a new expense entry"""
        print("\n--- Add New Expense ---")
        
        try:
            # Get date
            date_str = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
            if not date_str:
                date = datetime.now().strftime("%Y-%m-%d")
            else:
                datetime.strptime(date_str, "%Y-%m-%d")  # Validate date
                date = date_str
            
            # Get amount
            amount = float(input("Enter amount: "))
            
            # Get category
            print("\nAvailable categories:")
            for i, category in enumerate(self.categories, 1):
                print(f"{i}. {category}")
            
            while True:
                try:
                    cat_choice = int(input("Select category (number): "))
                    if 1 <= cat_choice <= len(self.categories):
                        category = self.categories[cat_choice - 1]
                        break
                    else:
                        print("Invalid choice. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")
            
            # Get description
            description = input("Enter description: ").strip()
            
            # Create expense record
            expense = {
                'id': len(self.expenses) + 1,
                'date': date,
                'amount': amount,
                'category': category,
                'description': description
            }
            
            self.expenses.append(expense)
            self.save_data()
            print("✓ Expense added successfully!")
            
        except ValueError as e:
            print(f"Error: Invalid input - {e}")
        except Exception as e:
            print(f"Error adding expense: {e}")
    
    def view_all_expenses(self):
        """Display all expenses"""
        print("\n--- All Expenses ---")
        if not self.expenses:
            print("No expenses recorded yet.")
            return
        
        self.display_expenses(self.expenses)
    
    def view_expenses_by_date(self):
        """View expenses for a specific date"""
        print("\n--- View Expenses by Date ---")
        date = input("Enter date (YYYY-MM-DD): ").strip()
        
        try:
            datetime.strptime(date, "%Y-%m-%d")
            filtered = [exp for exp in self.expenses if exp['date'] == date]
            
            if filtered:
                print(f"\nExpenses for {date}:")
                self.display_expenses(filtered)
            else:
                print(f"No expenses found for {date}")
                
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
    
    def view_expenses_by_category(self):
        """View expenses for a specific category"""
        print("\n--- View Expenses by Category ---")
        print("Available categories:")
        for i, category in enumerate(self.categories, 1):
            print(f"{i}. {category}")
        
        try:
            cat_choice = int(input("Select category (number): "))
            if 1 <= cat_choice <= len(self.categories):
                category = self.categories[cat_choice - 1]
                filtered = [exp for exp in self.expenses if exp['category'] == category]
                
                if filtered:
                    print(f"\nExpenses for {category}:")
                    self.display_expenses(filtered)
                else:
                    print(f"No expenses found for {category}")
            else:
                print("Invalid category choice.")
        except ValueError:
            print("Please enter a valid number.")
    
    def search_expenses(self):
        """Search expenses by description or amount range"""
        print("\n--- Search Expenses ---")
        print("1. Search by description")
        print("2. Search by amount range")
        
        choice = input("Enter your choice (1-2): ").strip()
        
        if choice == '1':
            keyword = input("Enter search keyword: ").lower()
            filtered = [exp for exp in self.expenses if keyword in exp['description'].lower()]
            
            if filtered:
                print(f"\nFound {len(filtered)} expenses matching '{keyword}':")
                self.display_expenses(filtered)
            else:
                print(f"No expenses found matching '{keyword}'")
                
        elif choice == '2':
            try:
                min_amount = float(input("Enter minimum amount: "))
                max_amount = float(input("Enter maximum amount: "))
                
                filtered = [exp for exp in self.expenses if min_amount <= exp['amount'] <= max_amount]
                
                if filtered:
                    print(f"\nFound {len(filtered)} expenses between {min_amount} and {max_amount}:")
                    self.display_expenses(filtered)
                else:
                    print(f"No expenses found in the specified range.")
                    
            except ValueError:
                print("Invalid amount. Please enter numbers only.")
        else:
            print("Invalid choice.")
    
    def generate_monthly_report(self):
        """Generate monthly expense report"""
        print("\n--- Monthly Report ---")
        
        try:
            year_month = input("Enter year and month (YYYY-MM): ").strip()
            year, month = map(int, year_month.split('-'))
            
            # Filter expenses for the specified month
            monthly_expenses = []
            for exp in self.expenses:
                exp_date = datetime.strptime(exp['date'], "%Y-%m-%d")
                if exp_date.year == year and exp_date.month == month:
                    monthly_expenses.append(exp)
            
            if not monthly_expenses:
                print(f"No expenses found for {year_month}")
                return
            
            # Calculate totals
            total_amount = sum(exp['amount'] for exp in monthly_expenses)
            
            # Category breakdown
            category_totals = {}
            for exp in monthly_expenses:
                category = exp['category']
                category_totals[category] = category_totals.get(category, 0) + exp['amount']
            
            # Display report
            print(f"\n=== Monthly Report for {year_month} ===")
            print(f"Total Expenses: ${total_amount:.2f}")
            print(f"Number of Transactions: {len(monthly_expenses)}")
            
            print("\nCategory Breakdown:")
            for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
                percentage = (amount / total_amount) * 100
                print(f"  {category}: ${amount:.2f} ({percentage:.1f}%)")
            
            # Daily trend
            daily_totals = {}
            for exp in monthly_expenses:
                day = exp['date']
                daily_totals[day] = daily_totals.get(day, 0) + exp['amount']
            
            print(f"\nTop 5 Highest Spending Days:")
            for day, amount in sorted(daily_totals.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  {day}: ${amount:.2f}")
                
            # Ask if user wants to export
            export = input("\nExport this report to file? (y/n): ").lower()
            if export == 'y':
                self.export_report(monthly_expenses, year_month, total_amount, category_totals)
                
        except ValueError:
            print("Invalid date format. Please use YYYY-MM.")
        except Exception as e:
            print(f"Error generating report: {e}")
    
    def export_report(self, expenses, year_month, total_amount, category_totals):
        """Export report to CSV file"""
        try:
            filename = f"expense_report_{year_month}.csv"
            
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                
                # Write header
                writer.writerow(['Monthly Expense Report', year_month])
                writer.writerow(['Total Amount', f"${total_amount:.2f}"])
                writer.writerow(['Number of Transactions', len(expenses)])
                writer.writerow([])
                
                # Write category breakdown
                writer.writerow(['Category Breakdown'])
                writer.writerow(['Category', 'Amount', 'Percentage'])
                for category, amount in category_totals.items():
                    percentage = (amount / total_amount) * 100
                    writer.writerow([category, f"${amount:.2f}", f"{percentage:.1f}%"])
                
                writer.writerow([])
                
                # Write detailed expenses
                writer.writerow(['Detailed Expenses'])
                writer.writerow(['Date', 'Amount', 'Category', 'Description'])
                for exp in expenses:
                    writer.writerow([
                        exp['date'],
                        f"${exp['amount']:.2f}",
                        exp['category'],
                        exp['description']
                    ])
            
            print(f"✓ Report exported to {filename}")
            
        except Exception as e:
            print(f"Error exporting report: {e}")
    
    def display_expenses(self, expenses_list):
        """Display a list of expenses in formatted table"""
        if not expenses_list:
            print("No expenses to display.")
            return
        
        print("-" * 80)
        print(f"{'ID':<4} {'Date':<12} {'Amount':<10} {'Category':<15} {'Description'}")
        print("-" * 80)
        
        total = 0
        for exp in expenses_list:
            print(f"{exp['id']:<4} {exp['date']:<12} ${exp['amount']:<9.2f} {exp['category']:<15} {exp['description']}")
            total += exp['amount']
        
        print("-" * 80)
        print(f"Total: ${total:.2f}")
        print(f"Number of expenses: {len(expenses_list)}")
    
    def show_statistics(self):
        """Show basic statistics"""
        if not self.expenses:
            print("No expenses recorded yet.")
            return
        
        total_amount = sum(exp['amount'] for exp in self.expenses)
        avg_amount = total_amount / len(self.expenses)
        
        # Most expensive expense
        most_expensive = max(self.expenses, key=lambda x: x['amount'])
        
        # Category statistics
        category_counts = {}
        for exp in self.expenses:
            category_counts[exp['category']] = category_counts.get(exp['category'], 0) + 1
        
        print("\n--- Statistics ---")
        print(f"Total Expenses: ${total_amount:.2f}")
        print(f"Average per Expense: ${avg_amount:.2f}")
        print(f"Most Expensive: ${most_expensive['amount']:.2f} ({most_expensive['category']} - {most_expensive['description']})")
        print(f"Total Records: {len(self.expenses)}")
        
        print("\nCategories by count:")
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {category}: {count} expenses")

def main():
    """Main function to run the expense tracker"""
    tracker = ExpenseTracker()
    
    while True:
        print("\n" + "="*50)
        print("      DAILY EXPENSE TRACKER")
        print("="*50)
        print("1. Add New Expense")
        print("2. View All Expenses")
        print("3. View Expenses by Date")
        print("4. View Expenses by Category")
        print("5. Search Expenses")
        print("6. Generate Monthly Report")
        print("7. Show Statistics")
        print("8. Exit")
        print("-"*50)
        
        choice = input("Enter your choice (1-8): ").strip()
        
        try:
            if choice == '1':
                tracker.add_expense()
            elif choice == '2':
                tracker.view_all_expenses()
            elif choice == '3':
                tracker.view_expenses_by_date()
            elif choice == '4':
                tracker.view_expenses_by_category()
            elif choice == '5':
                tracker.search_expenses()
            elif choice == '6':
                tracker.generate_monthly_report()
            elif choice == '7':
                tracker.show_statistics()
            elif choice == '8':
                print("Thank you for using Expense Tracker! Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number between 1-8.")
        
        except Exception as e:
            print(f"An error occurred: {e}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()