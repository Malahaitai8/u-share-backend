import pandas as pd
from pathlib import Path

def merge_dustbins_data():
    dustbins_path = Path("services/guide_service/data/dustbins.xlsx")
    station_info_path = Path("垃圾站点信息表.xlsx")
    output_path = Path("services/guide_service/data/dustbins_with_types.xlsx")

    dustbins_df = pd.read_excel(dustbins_path)
    station_info_df = pd.read_excel(station_info_path)

    dustbins_df.columns = dustbins_df.columns.str.strip()
    station_info_df.columns = station_info_df.columns.str.strip()

    dustbins_name_col = dustbins_df.columns[2]
    station_name_col = station_info_df.columns[2]

    merge_df = pd.merge(
        dustbins_df,
        station_info_df[[station_name_col, station_info_df.columns[3], station_info_df.columns[4], station_info_df.columns[5], station_info_df.columns[6]]],
        left_on=dustbins_name_col,
        right_on=station_name_col,
        how="left"
    )

    merge_df = merge_df.drop(columns=[station_name_col])

    new_col_names = [dustbins_df.columns[0], dustbins_df.columns[1], dustbins_name_col, "其他", "可回收", "厨余", "有害"]
    merge_df.columns = new_col_names

    merge_df.to_excel(output_path, index=False)
    print(f"合并完成！输出文件: {output_path}")
    print(f"列名: {merge_df.columns.tolist()}")
    print(f"共 {len(merge_df)} 条记录")
    has_data = merge_df[(merge_df['可回收'] > 0) | (merge_df['厨余'] > 0) | (merge_df['有害'] > 0)]
    print(f"有垃圾桶数据的行数: {len(has_data)}")
    if len(has_data) > 0:
        print(has_data.head(10))

if __name__ == "__main__":
    merge_dustbins_data()
