import streamlit as st
import pandas as pd
from sheets import *
from split_wise import *
import datetime

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

def calculate_each_cost(df, names, birthday):
    names.remove("All")
    name_cost_dict = {name: 0.00 for name in names}
    for index, row in df.iterrows():
        if "All" in row["People"]:
            cost = round(row["Cost"] / len(names), 2)
            for name in names:
                name_cost_dict[name] += cost
        else:
            cost = round(row["Cost"] / len(row["People"]), 2)
            for name in row["People"]:
                name_cost_dict[name] += cost
    if birthday is not None:
        birthday_split = name_cost_dict[birthday] / (len(names) - 1)
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
    print(receipt_df)
    print(cost_df)
    if place is None:
        st.error("Please enter a name for the place")
    else:
        send_to_sheets(receipt_df, cost_df, date, place)
        if use_splitwise:
            send_info_to_splitwise(cost_df, payer, group_name, total_cost, place, date)
        st.session_state.df2 = create_initial_df2()
        st.session_state.df = create_initial_df()
        print(st.session_state.df)

def handle_change(df, names, birthday):
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
    date = st.date_input("Date", format="MM/DD/YYYY", max_value=today)
    place = st.text_input("Place")
    are_names_entered = st.checkbox("Are all names entered?")
    names = st.text_input("Enter First Name (split by commas and space): ", disabled=are_names_entered, key="names")
    name_arr = names.strip().split(", ")
    name_arr.append("All")

    with st.sidebar:
        st.header("New Cost Addition")
        with st.form(key="hello_world", clear_on_submit=True):
            # Input fields for new row data
            new_name = st.text_input('Name', value=st.session_state.new_name)
            new_cost = st.number_input('Cost', placeholder=0.00)
            new_people = st.multiselect(
                'People Responsible:',
                options=name_arr
            )
            if "All" in new_people:
                new_people = ["All"]
            # Add row button
            if st.form_submit_button('Add'):
                if new_name and len(new_people) > 0 and new_cost > 0:
                    new_row = {'Name': new_name, 'Cost': new_cost, 'People': new_people}
                    df = st.session_state.df._append(new_row, ignore_index=True)
                    st.session_state.df = df
                    clear_cost()
                else:
                    st.sidebar.error("Please fix the errors")

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
    # Display the editable DataFrame
    edited_df = st.data_editor(st.session_state.df, width=800, hide_index=True, num_rows="dynamic")
    print(edited_df)
    # Handle changes made to the DataFrame
    if edited_df is not None:
        print("here")
        st.session_state.df = edited_df

    total_cost = sum(st.session_state.df["Cost"])
    st.write(f"Total Cost: ${total_cost:.2f}")

    if not is_birthday:
        birthday = None
    if len(name_arr) > 1:
        st.session_state.df2 = calculate_each_cost(st.session_state.df, name_arr, birthday)
        st.dataframe(st.session_state.df2, width=800, hide_index=True)

    if st.button("Save"):
        on_click(st.session_state.df, st.session_state.df2, date, place, payer, use_splitwise, splitwise_group_name, total_cost)

if __name__ == '__main__':
    main()
