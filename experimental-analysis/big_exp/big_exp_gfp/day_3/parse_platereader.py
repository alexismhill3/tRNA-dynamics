import pandas as pd
import openpyxl as xl
from rich import print
import numbers

well_encoding = {'D6': ['B2', 'GFP10', 'RBS0.125', 24.802324968961695, 169.1976750310383], 'C10': ['B2', 'GFP10', 'RBS0.125', 24.802324968961695, 169.1976750310383], 'G8': ['C2', 'GFP25', 'RBS0.125', 22.47302474917753, 171.52697525082246], 'D9': ['C2', 'GFP25', 'RBS0.125', 22.47302474917753, 171.52697525082246], 'D4': ['D2', 'GFP50', 'RBS0.125', 27.45972099677744, 166.54027900322257], 'D5': ['D2', 'GFP50', 'RBS0.125', 27.45972099677744, 166.54027900322257], 'G9': ['E2', 'GFP75', 'RBS0.125', 30.475110891091468, 163.52488910890852], 'D2': ['E2', 'GFP75', 'RBS0.125', 30.475110891091468, 163.52488910890852], 'B3': ['B3', 'GFP10', 'RBS0.25', 20.6522235401309, 173.3477764598691], 'E2': ['B3', 'GFP10', 'RBS0.25', 20.6522235401309, 173.3477764598691], 'F5': ['C3', 'GFP25', 'RBS0.25', 21.031927614483102, 172.9680723855169], 'C8': ['C3', 'GFP25', 'RBS0.25', 21.031927614483102, 172.9680723855169], 'B4': ['D3', 'GFP50', 'RBS0.25', 25.37943915759807, 168.62056084240191], 'D7': ['D3', 'GFP50', 'RBS0.25', 25.37943915759807, 168.62056084240191], 'C3': ['E3', 'GFP75', 'RBS0.25', 30.278372877739713, 163.7216271222603], 'F10': ['E3', 'GFP75', 'RBS0.25', 30.278372877739713, 163.7216271222603], 'F9': ['B4', 'GFP10', 'RBS0.5', 23.42717186429252, 170.57282813570748], 'B11': ['B4', 'GFP10', 'RBS0.5', 23.42717186429252, 170.57282813570748], 'G11': ['C4', 'GFP25', 'RBS0.5', 20.60685456366883, 173.39314543633117], 'B9': ['C4', 'GFP25', 'RBS0.5', 20.60685456366883, 173.39314543633117], 'G6': ['D4', 'GFP50', 'RBS0.5', 25.50364527776358, 168.49635472223642], 'C9': ['D4', 'GFP50', 'RBS0.5', 25.50364527776358, 168.49635472223642], 'G4': ['E4', 'GFP75', 'RBS0.5', 19.822992513823134, 174.17700748617688], 'F11': ['E4', 'GFP75', 'RBS0.5', 19.822992513823134, 174.17700748617688], 'C2': ['B5', 'GFP10', 'RBS1', 24.828585152567776, 169.17141484743223], 'C6': ['B5', 'GFP10', 'RBS1', 24.828585152567776, 169.17141484743223], 'B7': ['C5', 'GFP25', 'RBS1', 18.249495140075457, 175.75050485992455], 'E9': ['C5', 'GFP25', 'RBS1', 18.249495140075457, 175.75050485992455], 'G5': ['D5', 'GFP50', 'RBS1', 24.504283161964345, 169.49571683803566], 'F6': ['D5', 'GFP50', 'RBS1', 24.504283161964345, 169.49571683803566], 'F2': ['E5', 'GFP75', 'RBS1', 21.753803269454018, 172.246196730546], 'F3': ['E5', 'GFP75', 'RBS1', 21.753803269454018, 172.246196730546], 'G7': ['B6', 'GFP10', 'RBS2', 29.590661957039284, 164.4093380429607], 'C4': ['B6', 'GFP10', 'RBS2', 29.590661957039284, 164.4093380429607], 'C5': ['C6', 'GFP25', 'RBS2', 19.308851308806805, 174.6911486911932], 'B2': ['C6', 'GFP25', 'RBS2', 19.308851308806805, 174.6911486911932], 'E8': ['D6', 'GFP50', 'RBS2', 26.603062057401182, 167.3969379425988], 'E5': ['D6', 'GFP50', 'RBS2', 26.603062057401182, 167.3969379425988], 'C7': ['E6', 'GFP75', 'RBS2', 21.328422109151145, 172.67157789084885], 'D10': ['E6', 'GFP75', 'RBS2', 21.328422109151145, 172.67157789084885], 'E11': ['B7', 'GFP10', 'RBS4', 23.415477366991134, 170.58452263300887], 'D8': ['B7', 'GFP10', 'RBS4', 23.415477366991134, 170.58452263300887], 'B6': ['C7', 'GFP25', 'RBS4', 19.277105846322616, 174.72289415367737], 'E3': ['C7', 'GFP25', 'RBS4', 19.277105846322616, 174.72289415367737], 'G10': ['D7', 'GFP50', 'RBS4', 21.78411412397232, 172.21588587602767], 'G3': ['D7', 'GFP50', 'RBS4', 21.78411412397232, 172.21588587602767], 'F8': ['E7', 'GFP75', 'RBS4', 20.49877750300502, 173.50122249699498], 'D3': ['E7', 'GFP75', 'RBS4', 20.49877750300502, 173.50122249699498], 'B5': ['blank', 'blank', 'blank', 0, 194], 'B8': ['blank', 'blank', 'blank', 0, 194], 'B10': ['blank', 'blank', 'blank', 0, 194], 'C11': ['blank', 'blank', 'blank', 0, 194], 'D11': ['blank', 'blank', 'blank', 0, 194], 'E4': ['blank', 'blank', 'blank', 0, 194], 'E6': ['blank', 'blank', 'blank', 0, 194], 'E7': ['blank', 'blank', 'blank', 0, 194], 'E10': ['blank', 'blank', 'blank', 0, 194], 'F4': ['blank', 'blank', 'blank', 0, 194], 'F7': ['blank', 'blank', 'blank', 0, 194], 'G2': ['blank', 'blank', 'blank', 0, 194]}

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
    merged_dataframe = merged_dataframe[['time', 'well', 'iptg', 'strain', 'rbs', 'temp', 'OD600', 'fluor', 'GFP_high', 'GFP_low']]


    # Find the average of the blanks at each timepoint
    blank_df = merged_dataframe[merged_dataframe['rbs'] == 'blank']
    blank_df = blank_df[['time', 'OD600', 'GFP_high', 'GFP_low']]
    blank_df = blank_df.groupby(by='time').mean()
    blank_df = blank_df.reset_index()
    print(blank_df.head())

    # Subtract the blank from the other data
    merged_dataframe = merged_dataframe[merged_dataframe['rbs'] != 'blank']
    merged_dataframe = pd.merge(merged_dataframe, blank_df, on='time', suffixes=('', '_blank'))
    merged_dataframe['OD600'] = merged_dataframe['OD600'] - merged_dataframe['OD600_blank']
    merged_dataframe['GFP_high'] = merged_dataframe['GFP_high'] - merged_dataframe['GFP_high_blank']
    merged_dataframe['GFP_low'] = merged_dataframe['GFP_low'] - merged_dataframe['GFP_low_blank']
    merged_dataframe = merged_dataframe.drop(columns=['OD600_blank', 'GFP_high_blank', 'GFP_low_blank'])

    # Drop the blank from the table
    merged_dataframe = merged_dataframe[merged_dataframe.rbs != 'blank']


    #print(merged_dataframe.head())
    return merged_dataframe, start_time


def main():
    file = "122223_post.xlsx"

    categories = ['GFP_high', 'GFP_low', 'OD600']

    data = parse_platereader(file, categories)

    # write clean data as a csv
    data[0].to_csv('day_3_gfp_clean.csv', index=False)

    data[0].head()


if __name__ == '__main__':
    main()


# EOF
