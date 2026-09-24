import pandas as pd
import numpy as np


segment_data = {
    "G": {"mass_fraction": 0.07, "cog_fraction": None},
    "tulow": {"mass_fraction": 0.43, "cog_fraction": 0.44},
    "ramie": {"mass_fraction": 0.03, "cog_fraction": 0.47},
    "przedramie": {"mass_fraction": 0.02, "cog_fraction": 0.42},
    "reka": {"mass_fraction": 0.01, "cog_fraction": None},
    "udo": {"mass_fraction": 0.12, "cog_fraction": 0.44},
    "podudzie": {"mass_fraction": 0.05, "cog_fraction": 0.42},
    "stopa": {"mass_fraction": 0.02, "cog_fraction": 0.44},
}


def compute_segment_cog(start, end, fraction):
    start = np.array(start)
    end = np.array(end)
    return start + fraction * (end - start)

def compute_frame_cog(row, frame_width, frame_height):
  
    keys = np.unique(['_'.join(col.split('_')[:-1]) for col in row.index if "_x" in col])
    landmarks = {}
    for key in keys:
        x = row[f"{key}_x"] * frame_width
        y = row[f"{key}_y"] * frame_height
        landmarks[key] = (x, y)

    # segment cogs prawa stwona tylko 
    segment_cogs = {}

    # G = głowa
    segment_cogs["G"] = landmarks["RIGHT_EYE_INNER"]

    # Tułów
    segment_cogs["tulow"] = compute_segment_cog(
        landmarks["RIGHT_SHOULDER"], landmarks["RIGHT_HIP"], segment_data["tulow"]["cog_fraction"]
    )

    # Ramiona
    segment_cogs["prawe_ramie"] = compute_segment_cog(
        landmarks["RIGHT_SHOULDER"], landmarks["RIGHT_ELBOW"], segment_data["ramie"]["cog_fraction"]
    )
    segment_cogs["lewe_ramie"] = segment_cogs["prawe_ramie"]  # uproszczenie: brak LEFT_ danych

    # Przedramiona
    segment_cogs["prawe_przedramie"] = compute_segment_cog(
        landmarks["RIGHT_ELBOW"], landmarks["RIGHT_WRIST"], segment_data["przedramie"]["cog_fraction"]
    )
    segment_cogs["lewe_przedramie"] = segment_cogs["prawe_przedramie"]

    # Ręce (indeks palca)
    segment_cogs["prawa_reka"] = landmarks["RIGHT_INDEX"]
    segment_cogs["lewa_reka"] = landmarks["RIGHT_INDEX"]

    # Uda
    segment_cogs["prawe_udo"] = compute_segment_cog(
        landmarks["RIGHT_HIP"], landmarks["RIGHT_KNEE"], segment_data["udo"]["cog_fraction"]
    )
    segment_cogs["lewe_udo"] = segment_cogs["prawe_udo"]

    # Podudzia
    segment_cogs["prawe_podudzie"] = compute_segment_cog(
        landmarks["RIGHT_KNEE"], landmarks["RIGHT_ANKLE"], segment_data["podudzie"]["cog_fraction"]
    )
    segment_cogs["lewe_podudzie"] = segment_cogs["prawe_podudzie"]

    # Stopy
    segment_cogs["prawa_stopa"] = compute_segment_cog(
        landmarks["RIGHT_ANKLE"], landmarks["RIGHT_FOOT_INDEX"], segment_data["stopa"]["cog_fraction"]
    )
    segment_cogs["lewa_stopa"] = segment_cogs["prawa_stopa"]

    # suma 
    total_mass = 0
    sum_x = 0
    sum_y = 0

    for seg in segment_cogs:
        typ = seg.split("_")[-1]  # np. "udo"
        mass_frac = segment_data[typ]["mass_fraction"]
        x, y = segment_cogs[seg]
        sum_x += x * mass_frac
        sum_y += y * mass_frac
        total_mass += mass_frac

    cog_x = sum_x / total_mass
    cog_y = sum_y / total_mass
    return cog_x, cog_y

def calculate_cog_for_csv(csv_path, frame_width, frame_height, output_csv_path=None):
    df = pd.read_csv(csv_path)
    cog_x_list = []
    cog_y_list = []

    for _, row in df.iterrows():
        cog_x, cog_y = compute_frame_cog(row, frame_width, frame_height)
        cog_x_list.append(cog_x)
        cog_y_list.append(cog_y)

    df["com_x"] = cog_x_list
    df["com_y"] = cog_y_list

    if output_csv_path:
        df.to_csv(output_csv_path, index=False)

    return df[["frame", "com_x", "com_y"]]

if __name__ == "__main__":
    video_width = 1920
    video_height = 1080
    csv_path = "P001_kolana.MP4.csv"
    output_path = "P001_kolana_com.csv"
    df_cog = calculate_cog_for_csv(csv_path, video_width, video_height, output_path)
    print(df_cog.head())
