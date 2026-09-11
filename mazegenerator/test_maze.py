from mazegenerator import MazeGenerator

WALL_N, WALL_E, WALL_S, WALL_W = 1, 2, 4, 8


def print_maze(cells: list[list[int]]) -> None:
    for row in cells:
        top = ""
        mid = ""
        for cell in row:
            top += "+" + ("----" if cell & WALL_N else "    ")
            mid += ("|" if cell & WALL_W else " ") + "    "
        print(top + "+")
        print(mid + ("|" if row[-1] & WALL_E else " "))
    bottom = "".join(
        "+" + ("----" if cell & WALL_S else "    ") for cell in cells[-1]
    )
    print(bottom + "+")


def main() -> None:
    gen = MazeGenerator(size=(15, 15), perfect=False, seed=42)

    print("Type of .maze:", type(gen.maze))
    print("Grid dimensions (rows, cols):", len(gen.maze), len(gen.maze[0]))
    print("First row raw values:", gen.maze[0])
    print()
    print("Entry:", gen.maze_entry)
    print("Exit:", gen.maze_exit)
    print("Shortest path (N/E/S/W string):", gen.shortest_path)
    print()
    print_maze(gen.maze)


if __name__ == "__main__":
    main()