import os
import sys
import pandas as pd

# =========================================================
# 🛡️ SYSTEM TERMINAL ENVIRONMENT CONFIGURATION
# =========================================================
# Force the system environment to completely turn off the broken PyREPL engine
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHON_BASIC_REPL"] = "1"

# Force standard I/O streams to ignore bad surrogate bytes if printed
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='backslashreplace')


def safe_decode_text(text_input) -> str:
    """
    Directly drops high/low split surrogate codes (0xD800 to 0xDFFF) 
    by reading individual character ordinal values before errors occur.
    """
    if text_input is None:
        return ""
    text_str = str(text_input)
    # Filter out characters inside the illegal surrogate unicode block
    return "".join(c for c in text_str if not (0xD800 <= ord(c) <= 0xDFFF))


# =========================================================
# 🧮 HVAC CALCULATIONS
# =========================================================
def calculate_sensible_load(cfm: float, entering_db: float, leaving_db: float) -> dict:
    """Standard Equation: Q = CFM * 1.08 * (T_entering - T_leaving)"""
    if leaving_db >= entering_db:
        raise ValueError("Leaving temperature must be lower than Entering temperature.")
        
    delta_t = entering_db - leaving_db
    sensible_load_btuh = cfm * 1.08 * delta_t
    cooling_tons = sensible_load_btuh / 12000
    
    return {
        "delta_t_f": round(delta_t, 1),
        "load_btuh": round(sensible_load_btuh, 2),
        "load_tons": round(cooling_tons, 2)
    }


# =========================================================
# 📊 LOCAL SPREADSHEET AUTOMATION ENGINE
# =========================================================
def process_hvac_sheet(file_path: str):
    """Loads, cleans, and runs summary evaluations on engineering files."""
    cleaned_path = safe_decode_text(file_path).strip("'\"")
    
    if not os.path.exists(cleaned_path):
        print(f"\n[Error] Target document not found at: {cleaned_path}")
        return

    try:
        # Load sheets based on formatting rules
        if cleaned_path.lower().endswith('.csv'):
            df = pd.read_csv(cleaned_path)
        elif cleaned_path.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(cleaned_path)
        else:
            print("\n[Error] Invalid format. Provide a standard CSV or Excel file.")
            return
            
        # Scrub all headers and object columns against surrogate entries
        df.columns = [safe_decode_text(col) for col in df.columns]
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).apply(safe_decode_text)
            
        print("\n=== File Analysis Processed Safely ===")
        print(df.head(5))
        print("=======================================")
        
    except Exception as e:
        print(f"\n[Pipeline Failure] Processing aborted: {str(e)}")


# =========================================================
# 🎮 SYSTEM ENGINE INTERACTIVE TERMINAL MENU
# =========================================================
def main():
    while True:
        print("\n" + "="*40)
        print("      NORMAL HVAC DATA INTERFACE        ")
        print("="*40)
        print("1. Compute Manual Sensible Load")
        print("2. Batch Process Excel / CSV Sheet")
        print("3. Shut Down System")
        print("="*40)
        
        user_selection = input("Select Option (1-3): ").strip()
        
        if user_selection == '1':
            try:
                air_cfm = float(input("Enter Volume (CFM): "))
                temp_in = float(input("Enter Entering Temp (F): "))
                temp_out = float(input("Enter Leaving Temp (F): "))
                
                output = calculate_sensible_load(air_cfm, temp_in, temp_out)
                print(f"\nResults:\n Delta T: {output['delta_t_f']} F\n Load: {output['load_btuh']:,} BTUH\n Sizing Sched: {output['load_tons']} TR")
            except Exception as error_msg:
                print(f"\nCalculation Input Error: {safe_decode_text(error_msg)}")
                
        elif user_selection == '2':
            input_path = input("Enter File Path or Drag File Here: ")
            process_hvac_sheet(input_path)
            
        elif user_selection == '3':
            print("\nSystems terminated successfully.")
            break
        else:
            print("\nInvalid operation window range selected.")

if __name__ == "__main__":
    main()
