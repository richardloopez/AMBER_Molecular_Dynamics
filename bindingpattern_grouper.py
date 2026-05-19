from pathlib import Path
import csv
import readline
readline.parse_and_bind("tab: complete")


def frames_to_ranges(frames):
    if not frames:
        return ""
    frames_sorted = sorted(int(f) for f in frames)
    ranges = []
    start = frames_sorted[0]
    prev = frames_sorted[0]
    for num in frames_sorted[1:]:
        if num == prev + 1:
            prev = num
        else:
            if start == prev:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{prev}")
            start = num
            prev = num
    if start == prev:
        ranges.append(str(start))
    else:
        ranges.append(f"{start}-{prev}")
    return ",".join(ranges)


document = input("Please enter the path to the csv file: ")
result_name = f"{document.split('.')[0]}_grouped_frames.csv"
path = Path(document)


groups = {}


with open(path, 'r', newline='') as f:
    csv_reader = csv.reader(f)
    header = next(csv_reader, None)
    
    for row in csv_reader:
        frame = row[0]
        binding_pattern = tuple(int(x) for x in row[1:])
        
        if binding_pattern not in groups:
            groups[binding_pattern] = []
        groups[binding_pattern].append(frame)


with open(result_name, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["binding_pattern", "frames"])
    
    for binding_pattern, frames in groups.items():
        pattern_str = ",".join(str(x) for x in binding_pattern)
        frames_str = frames_to_ranges(frames)  
        writer.writerow([pattern_str, frames_str])

if Path(result_name).exists():
    print(f"File {result_name} generated successfully.")
else:
    print(f"Error: File {result_name} was not generated.")
