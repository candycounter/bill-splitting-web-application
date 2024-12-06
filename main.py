import streamlit as st
import pandas as pd
from sheets import *
from split_wise import *
import datetime
from tax import *
# Initialize or create the DataFrame
def create_initial_df():
    return pd.DataFrame({
        'Name': [],
        "Cost": [],
        'People': []  # Empty lists for multi-select options
    })

def create_initial_df2():
    return pd.DataFrame({
        'Name': [],
        'Cost': []
    })

def calculate_each_cost(df, names, birthday, subtotal):
    name_cost_dict = {name: 0.00 for name in names}
    new_total = subtotal
    for index, row in df.iterrows():
        if row["Name"] != "Tax" and row["Name"] != "Tip":
            if "All" in row["People"]:
                cost = round(row["Cost"] / len(names), 2)
                for name in names:
                    name_cost_dict[name] += cost
            else:
                cost = round(row["Cost"] / len(row["People"]), 2)
                for name in row["People"]:
                    name_cost_dict[name] += cost
        else:
            cost = 0
            tip_cost = 0
            print(names)
            print(row["Cost"])
            print("NAME: " + row["Name"])
            for name in names:
                print("____________________")
                print("Name: " + name)
                print(name_cost_dict[name])
                print("TT: " + str(subtotal))
                split = round((name_cost_dict[name] / new_total) * row["Cost"], 2)
                tip_cost += split
                print("Tip Split: " + str(split))
                calc = round((name_cost_dict[name] / new_total) * row["Cost"], 2)
                print("Calc: " + str(calc))
                name_cost_dict[name] += calc
                print("New Cost: " + str(name_cost_dict[name]))
                cost += name_cost_dict[name]
            print("Tip Cost: " + str(tip_cost))
            print("Cost: " + str(cost))
            new_total += tip_cost
    if birthday is not None:
        birthday_split = round(name_cost_dict[birthday] / (len(names) - 1), 2)
        for name in names:
            if name == birthday:
                name_cost_dict[name] = 0
            else:
                name_cost_dict[name] += birthday_split
    return pd.DataFrame({
        "Name": name_cost_dict.keys(),
        "Cost": name_cost_dict.values()
    })

def on_click(receipt_df, cost_df, date, place, payer, use_splitwise, group_name, total_cost):
    # print(receipt_df)
    # print(cost_df)
    
    df_cost = round(sum(cost_df["Cost"]), 2)
    print("__________COST___________________")
    print(df_cost)
    if df_cost != total_cost:
        print("I reached here")
        diff = round(total_cost - df_cost, 2)
        print("Diff: " + str(diff))
        # print(len(cost_df))
        cost_df = cost_df.sort_values(by="Cost", ascending=diff > 0, ignore_index=True)
        # print("---------")
        # print(cost_df)
        index = 0
        while abs(diff) > 0:
            if cost_df.at[index, 'Cost'] > 0.00:
                if diff > 0:
                    cost_df.at[index, 'Cost'] += 0.01
                    diff = ((diff * 100) - 1) / 100
                else:
                    cost_df.at[index, 'Cost'] -= 0.01
                    diff = ((diff * 100) + 1) / 100
            index = (index + 1) % len(cost_df)
        print(cost_df)
                
        
        
    if place is None:
        st.error("Please enter a name for the place")
    else:
        send_to_sheets(receipt_df, cost_df, date, place, total_cost, payer)
        if use_splitwise:
            send_info_to_splitwise(cost_df, payer, group_name, total_cost, place, date)
        # st.session_state.df2 = create_initial_df2()
        # st.session_state.df = create_initial_df()
        print(st.session_state.df)
def handle_change(df, names, birthday, total_cost):
    calculate_each_cost(df, names, birthday)

def main():
    if "new_name" not in st.session_state:
        st.session_state.new_name = ""
    if "new_cost" not in st.session_state:
        st.session_state.new_cost = 0.00
    if "new_people" not in st.session_state:
        st.session_state.new_people = [] 

    def clear_cost():
        st.session_state.new_name = ""
        st.session_state.new_cost = 0.00
        st.session_state.new_people = []

    st.title('Bill Splitter')

    # Initialize the DataFrame in the session state
    if 'df' not in st.session_state:
        st.session_state.df = create_initial_df()
    if 'df2' not in st.session_state:
        st.session_state.df2 = create_initial_df2()

    df = st.session_state.df
    today = datetime.date.today()
    date = st.date_input("Date", format="MM/DD/YYYY", max_value=today).strftime("%m/%d/%y")
    print("Date: " + str(date))
    place = st.text_input("Place")
    are_names_entered = st.checkbox("Are all names entered?")
    names = st.text_input("Enter First Name (split by commas and space): ", disabled=are_names_entered, key="names")
    name_arr = names.strip().split(", ")
    zip_code = st.text_input("Enter Zip Code (Tax Purposes)")
    if len(zip_code) > 0:
        tax_str = str(grab_tax_percentage(zip_code))
        tax_percentage = float(tax_str)
    with st.sidebar:
        st.header("New Cost Addition")
        # Input fields for new row data
        with st.form(key="form", clear_on_submit=True):
            new_name = st.text_input('Name', value=st.session_state.new_name)
            new_cost = st.number_input('Cost', placeholder=0.00)
            all_selected = st.checkbox("Is this cost for everyone?")
            new_people = st.multiselect(
                'People Responsible:',
                options=name_arr
            )
                
            # Add row button
            if st.form_submit_button('Add'):
                if all_selected:
                    new_people = ["All"]
                if new_name and len(new_people) > 0 and new_cost > 0:
                    new_row = {'Name': new_name, 'Cost': new_cost, 'People': new_people}
                    df = st.session_state.df._append(new_row, ignore_index=True)
                    st.session_state.df = df
                    
                    
                    # cost = round(sum(st.session_state.df['Cost'] * tax_percentage), 2)
                    # print(cost)
                    # new_row = pd.DataFrame({'Name': ['Tax'], 'Cost': [cost], 'People': [['All']]})
                    # st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                    print("After")
                    print(st.session_state.df)
                    clear_cost()
                    
                else:
                    st.sidebar.error("Please fix the errors")
        # Add tax input
    is_birthday = st.sidebar.checkbox("Is there a birthday: ")
    birthday = st.sidebar.selectbox(
        'Birthday',
        options=name_arr,
        placeholder="Choose an option",
        disabled=not is_birthday,
        key="birthday"
    )
    payer = st.sidebar.selectbox("Payer", options=name_arr)
    use_splitwise = st.sidebar.checkbox("Add to Splitwise: ")
    splitwise_group_name = st.sidebar.text_input(
        'Splitwise Group Name',
        placeholder="Enter Name",
        disabled=not use_splitwise,
        key="splitwise"
    )
    edited_df = st.data_editor(st.session_state.df, width=800, hide_index=True, num_rows="dynamic")
    print("EDDDDDD")
    print(edited_df)
        

    # Display the editable DataFrame
    st.session_state.df = edited_df
    
    print("Transition: ")
    print(st.session_state.df)

    # Calculate total cost including tax
    subtotal = sum(st.session_state.df[~st.session_state.df["Name"].isin(["Tax", "Tip"])]["Cost"])
    total_cost = sum(st.session_state.df["Cost"])
   # total_cost = subtotal * (1 + tax_percentage / 100)
    st.write(f"Subtotal: ${subtotal:.2f}")
    st.write(f"Total Cost: ${total_cost:.2f}")
    if not is_birthday:
        birthday = None
    if len(name_arr) > 1:
        st.session_state.df2 = calculate_each_cost(st.session_state.df, name_arr, birthday, subtotal)
        st.dataframe(st.session_state.df2, width=800, hide_index=True)

    if st.button("Save"):
        on_click(st.session_state.df, st.session_state.df2, date, place, payer, use_splitwise, splitwise_group_name, total_cost)

if __name__ == '__main__':
    main()
