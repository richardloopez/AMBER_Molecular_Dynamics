#!/usr/bin/env python3

# Author: Richard Lopez Corbalan
# GitHub: github.com/richardloopez
# Citation: If you use this code, please cite Lopez-Corbalan, R.

# Output file
output_file = "solvation_average.txt"

# Calculate the average for the first shell
with open("watershell.out.dat", "r") as file:
    lines = file.readlines()
    first_shell_sum = sum(float(line.split()[1]) for line in lines[1:])
    first_shell_avg = first_shell_sum / (len(lines) - 1)

# Calculate the average for the second shell
second_shell_sum = sum((float(line.split()[2]) - float(line.split()[1])) for line in lines[1:])
second_shell_avg = second_shell_sum / (len(lines) - 1)

# Write results to the output file
with open(output_file, "w") as file:
    file.write(f"Average first solvation shell: {first_shell_avg}\n")
    file.write(f"Average second solvation shell: {second_shell_avg}\n")

# Confirm to the user
print(f"File '{output_file}' generated with the averages of the solvation shells.")

