import pandas as pd
import re

def clean_property_data(input_file, output_file):
    """Clean and format property data for the Voice AI system"""
    
    # Read the original data
    df = pd.read_csv(input_file)
    
    print(f"Original data shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Clean numeric columns (remove $ and commas)
    numeric_columns = ['Rent/SF/Year', 'Annual Rent', 'Monthly Rent', 'GCI On 3 Years']
    
    for col in numeric_columns:
        if col in df.columns:
            # Remove $ signs and commas, convert to float
            df[col] = df[col].astype(str).str.replace('$', '').str.replace(',', '')
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Clean Size (SF) column
    if 'Size (SF)' in df.columns:
        df['Size (SF)'] = pd.to_numeric(df['Size (SF)'], errors='coerce')
    
    # Clean Floor column (extract numeric part)
    if 'Floor' in df.columns:
        df['Floor'] = df['Floor'].astype(str).str.extract('(\d+)')[0]
        df['Floor'] = pd.to_numeric(df['Floor'], errors='coerce')
    
    # Clean Suite column (keep as string but remove extra spaces)
    if 'Suite' in df.columns:
        df['Suite'] = df['Suite'].astype(str).str.strip()
    
    # Ensure unique_id is string
    if 'unique_id' in df.columns:
        df['unique_id'] = df['unique_id'].astype(str)
    
    # Remove rows with missing critical data
    critical_columns = ['Property Address', 'Size (SF)', 'Rent/SF/Year']
    df = df.dropna(subset=critical_columns)
    
    print(f"Cleaned data shape: {df.shape}")
    print(f"Sample of cleaned data:")
    print(df.head())
    
    # Save cleaned data
    df.to_csv(output_file, index=False)
    print(f"Cleaned data saved to: {output_file}")
    
    return df

if __name__ == "__main__":
    # Clean your property data
    input_file = "data/HackathonInternalKnowledgeBase.csv"  # Your original file
    output_file = "data/properties.csv"  # Cleaned file for the system
    
    try:
        cleaned_df = clean_property_data(input_file, output_file)
        print("✅ Data cleaning completed successfully!")
        
        # Show some statistics
        print(f"\nData Summary:")
        print(f"Total properties: {len(cleaned_df)}")
        print(f"Average size: {cleaned_df['Size (SF)'].mean():.0f} SF")
        print(f"Average rent: ${cleaned_df['Rent/SF/Year'].mean():.2f}/SF/Year")
        print(f"Rent range: ${cleaned_df['Rent/SF/Year'].min():.2f} - ${cleaned_df['Rent/SF/Year'].max():.2f}")
        
    except Exception as e:
        print(f"❌ Error cleaning data: {e}")
        print("Please check your file path and format.")