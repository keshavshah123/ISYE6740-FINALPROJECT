import pandas as pd
import re

file_path = 'echo_exporter/ECHO_Exporter.csv'

columns_to_keep = [
    'REGISTRY_ID', 
    'FAC_NAME', 
    'FAC_NAICS_CODES',  
    'FAC_STATE',        
    'FAC_EPA_REGION',   
    'FAC_MAJOR_FLAG'    
]

data_types = {
    'FAC_STATE': 'category',
    'FAC_EPA_REGION': 'category'
    # Removed FAC_MAJOR_FLAG from 'category' temporarily to handle NaNs easier during filtering
}

chunk_size = 100000 
filtered_chunks = []

print("Processing ECHO Exporter in chunks...")

for i, chunk in enumerate(pd.read_csv(file_path, 
                                      chunksize=chunk_size, 
                                      usecols=columns_to_keep, 
                                      dtype=data_types, 
                                      low_memory=False)):
    
    # FILTER A: Robust NAICS Search
    # \b means "word boundary". This looks for 31, 32, or 33 followed by any 4 digits, anywhere in the string.
    # na=False ensures missing NAICS codes don't break the regex
    is_manufacturing = chunk['FAC_NAICS_CODES'].astype(str).str.contains(r'\b(?:31|32|33)\d{4}\b', regex=True, na=False)
    
    # FILTER B: Robust Non-Major Search
    # Instead of looking for 'N', we keep anything that is explicitly NOT 'Y' (captures 'N' and blanks/NaNs)
    is_small_proxy = chunk['FAC_MAJOR_FLAG'] != 'Y'
    
    # Apply both filters
    filtered_chunk = chunk[is_manufacturing & is_small_proxy]
    
    # DEBUGGING: Print the survival rate of this specific chunk
    print(f"Chunk {i+1}: {is_manufacturing.sum()} passed NAICS | {is_small_proxy.sum()} passed Major Flag | {len(filtered_chunk)} passed BOTH.")
    
    filtered_chunks.append(filtered_chunk)

# Recombine and save
final_df = pd.concat(filtered_chunks, ignore_index=True)
final_df.to_csv('ECHO_Filtered_Small_Manufacturing.csv', index=False)

print(f"\nData pipeline complete. Final sample size: {len(final_df)} small manufacturing facilities.")