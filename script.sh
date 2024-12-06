#!/bin/bash
rm token.json && python3 sheets.py && streamlit run main.py
