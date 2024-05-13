import pandas as pd
import openpyxl as xl
from rich import print
import numbers

well_encoding = {'D9': ['B2', 'MCH10', 'RBS0.125', 19.998379328306406, 174.0016206716936], 'G6': ['B2', 'MCH10', 'RBS0.125', 19.998379328306406, 174.0016206716936], 'E7': ['C2', 'MCH25', 'RBS0.125', 16.6124850878012, 177.3875149121988], 'C8': ['C2', 'MCH25', 'RBS0.125', 16.6124850878012, 177.3875149121988], 'E3': ['D2', 'MCH50', 'RBS0.125', 17.14068551230489, 176.85931448769512], 'D4': ['D2', 'MCH50', 'RBS0.125', 17.14068551230489, 176.85931448769512], 'B4': ['E2', 'MCH75', 'RBS0.125', 17.33710455187554, 176.66289544812446], 'C10': ['E2', 'MCH75', 'RBS0.125', 17.33710455187554, 176.66289544812446], 'B2': ['B3', 'MCH10', 'RBS0.25', 34.70948976881548, 159.29051023118453], 'B3': ['B3', 'MCH10', 'RBS0.25', 34.70948976881548, 159.29051023118453], 'C2': ['C3', 'MCH25', 'RBS0.25', 18.412484867232777, 175.58751513276724], 'F10': ['C3', 'MCH25', 'RBS0.25', 18.412484867232777, 175.58751513276724], 'D7': ['D3', 'MCH50', 'RBS0.25', 17.75047677678299, 176.249523223217], 'B11': ['D3', 'MCH50', 'RBS0.25', 17.75047677678299, 176.249523223217], 'F5': ['E3', 'MCH75', 'RBS0.25', 15.973162697106568, 178.02683730289343], 'C7': ['E3', 'MCH75', 'RBS0.25', 15.973162697106568, 178.02683730289343], 'C6': ['B4', 'MCH10', 'RBS0.5', 18.492339975836575, 175.5076600241634], 'G11': ['B4', 'MCH10', 'RBS0.5', 18.492339975836575, 175.5076600241634], 'D8': ['C4', 'MCH25', 'RBS0.5', 16.653776480153905, 177.3462235198461], 'E11': ['C4', 'MCH25', 'RBS0.5', 16.653776480153905, 177.3462235198461], 'G8': ['D4', 'MCH50', 'RBS0.5', 20.32774951341294, 173.67225048658707], 'E10': ['D4', 'MCH50', 'RBS0.5', 20.32774951341294, 173.67225048658707], 'D3': ['E4', 'MCH75', 'RBS0.5', 17.394973377798788, 176.60502662220122], 'G9': ['E4', 'MCH75', 'RBS0.5', 17.394973377798788, 176.60502662220122], 'C5': ['B5', 'MCH10', 'RBS1', 16.3347670459662, 177.6652329540338], 'C3': ['B5', 'MCH10', 'RBS1', 16.3347670459662, 177.6652329540338], 'G3': ['C5', 'MCH25', 'RBS1', 15.870468138496438, 178.12953186150355], 'E6': ['C5', 'MCH25', 'RBS1', 15.870468138496438, 178.12953186150355], 'E4': ['D5', 'MCH50', 'RBS1', 17.32429642659391, 176.67570357340608], 'C9': ['D5', 'MCH50', 'RBS1', 17.32429642659391, 176.67570357340608], 'G7': ['E5', 'MCH75', 'RBS1', 14.752283626215007, 179.24771637378498], 'F11': ['E5', 'MCH75', 'RBS1', 14.752283626215007, 179.24771637378498], 'D5': ['B6', 'MCH10', 'RBS2', 15.177154005077304, 178.8228459949227], 'F9': ['B6', 'MCH10', 'RBS2', 15.177154005077304, 178.8228459949227], 'B10': ['C6', 'MCH25', 'RBS2', 15.157533857202207, 178.8424661427978], 'D2': ['C6', 'MCH25', 'RBS2', 15.157533857202207, 178.8424661427978], 'C4': ['D6', 'MCH50', 'RBS2', 17.466231303269346, 176.53376869673065], 'B9': ['D6', 'MCH50', 'RBS2', 17.466231303269346, 176.53376869673065], 'F6': ['E6', 'MCH75', 'RBS2', 16.00587000867707, 177.99412999132292], 'D10': ['E6', 'MCH75', 'RBS2', 16.00587000867707, 177.99412999132292], 'E9': ['B7', 'MCH10', 'RBS4', 14.683008707811135, 179.31699129218887], 'F8': ['B7', 'MCH10', 'RBS4', 14.683008707811135, 179.31699129218887], 'C11': ['C7', 'MCH25', 'RBS4', 14.237291542083108, 179.7627084579169], 'G10': ['C7', 'MCH25', 'RBS4', 14.237291542083108, 179.7627084579169], 'D11': ['D7', 'MCH50', 'RBS4', 15.891977063102958, 178.10802293689704], 'F7': ['D7', 'MCH50', 'RBS4', 15.891977063102958, 178.10802293689704], 'B5': ['E7', 'MCH75', 'RBS4', 22.654848357917466, 171.34515164208253], 'G5': ['E7', 'MCH75', 'RBS4', 22.654848357917466, 171.34515164208253], 'B6': ['blank', 'blank', 'blank', 0, 194], 'B7': ['blank', 'blank', 'blank', 0, 194], 'B8': ['blank', 'blank', 'blank', 0, 194], 'D6': ['blank', 'blank', 'blank', 0, 194], 'E2': ['blank', 'blank', 'blank', 0, 194], 'E5': ['blank', 'blank', 'blank', 0, 194], 'E8': ['blank', 'blank', 'blank', 0, 194], 'F2': ['blank', 'blank', 'blank', 0, 194], 'F3': ['blank', 'blank', 'blank', 0, 194], 'F4': ['blank', 'blank', 'blank', 0, 194], 'G2': ['blank', 'blank', 'blank', 0, 194], 'G4': ['blank', 'blank', 'blank', 0, 194]}

for well, data in well_encoding.items():
    if isinstance(data[2], float):
        data[2] = data[2]/4
    well_encoding[well] = [str(data[1]), str(data[2])]
    print(well_encoding[well])



def is_empty(row):
    if not any(row):
        return True
    else:
        return False

def parse_platereader(filename, categories):
    wb =  xl.load_workbook(filename)
    ws = wb.active
    in_data = False
    dataframes = []
    timepoints = []
    temperature = []
    start_time = None
    for row in ws.rows:
        row_values = [cell.value for cell in row]

        if row_values[0] == 'Start Time':
            start_time = row_values[1]
            continue

        if row_values[0] in categories:
            in_data = row_values[0]
            df = pd.DataFrame(columns=['time', 'well', 'iptg', 'rbs' 'temp',  'fluor', 'strain', in_data])
            continue

        if in_data and is_empty(row_values):
            in_data = False
            # Save the data
            dataframes.append(df)
            continue

        if in_data:
            if row_values[0] == 'Cycle Nr.':
                continue
            elif row_values[0] == 'Time [s]':
                timepoints = row_values[1:]
                # Round timepoints to nearest second
                timepoints = [round(timepoint) for timepoint in timepoints if timepoint is not None]
                continue
            elif row_values[0] == 'Temp. [°C]':
                temperature = row_values[1:]
                temperature = [temp for temp in temperature if temp is not None]
                continue
            else:
                well = row_values[0]
                values = row_values[1:]
                values = [value for value in values if value is not None]
                #print(len(timepoints), len(values), len(temperature))
                if 'blank' in well_encoding[well][0]:
                    fluor = 'blank'
                elif 'G' in well_encoding[well][0]:
                    fluor = 'GFP'
                elif 'M' in well_encoding[well][0]:
                    fluor = 'mCherry'
                else:
                    fluor = 'unknown'
                temp_dataframe = pd.DataFrame({'time': timepoints, 'well': well, 'iptg':'0.01875', 'rbs':well_encoding[well][1], 'temp': temperature, 'fluor':fluor, 'strain': well_encoding[well][0], in_data: values})
                df = pd.concat([df, temp_dataframe], ignore_index=True)
                continue

        continue

    merged_dataframe = pd.concat(dataframes, axis=1)
    merged_dataframe = merged_dataframe.replace('OVER', float('inf'))
    merged_dataframe = merged_dataframe.groupby(by=merged_dataframe.columns, axis=1).apply(lambda g: g.mean(axis=1) if isinstance(g.iloc[0,0], numbers.Number) else g.iloc[:,0]) # https://stackoverflow.com/questions/40311987/pandas-mean-of-columns-with-the-same-names
    
    # Fix order
    merged_dataframe = merged_dataframe[['time', 'well', 'iptg', 'strain', 'rbs', 'temp', 'OD600', 'fluor', 'mCherry_high', 'mCherry_low']]


    # Find the average of the blanks at each timepoint
    blank_df = merged_dataframe[merged_dataframe['rbs'] == 'blank']
    blank_df = blank_df[['time', 'OD600', 'mCherry_high', 'mCherry_low']]
    blank_df = blank_df.groupby(by='time').mean()
    blank_df = blank_df.reset_index()
    print(blank_df.head())

    # Subtract the blank from the other data
    merged_dataframe = merged_dataframe[merged_dataframe['rbs'] != 'blank']
    merged_dataframe = pd.merge(merged_dataframe, blank_df, on='time', suffixes=('', '_blank'))
    merged_dataframe['OD600'] = merged_dataframe['OD600'] - merged_dataframe['OD600_blank']
    merged_dataframe['mCherry_high'] = merged_dataframe['mCherry_high'] - merged_dataframe['mCherry_high_blank']
    merged_dataframe['mCherry_low'] = merged_dataframe['mCherry_low'] - merged_dataframe['mCherry_low_blank']
    merged_dataframe = merged_dataframe.drop(columns=['OD600_blank', 'mCherry_high_blank', 'mCherry_low_blank'])

    # Drop the blank from the table
    merged_dataframe = merged_dataframe[merged_dataframe.rbs != 'blank']


    #print(merged_dataframe.head())
    return merged_dataframe, start_time


def main():
    file = "122923_post.xlsx"

    categories = ['mCherry_high', 'mCherry_low', 'OD600']

    data = parse_platereader(file, categories)

    # write clean data as a csv
    data[0].to_csv('day_3_mch_clean.csv', index=False)

    data[0].head()


if __name__ == '__main__':
    main()


# EOF
