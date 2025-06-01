import tkinter as tk
from queue import PriorityQueue
import random
import time
# Định nghĩa các hướng di chuyển: lên, xuống, trái, phải
UP = [1, 0]
DOWN = [-1, 0]
LEFT = [0, -1]
RIGHT = [0, 1]

class Node:
    def __init__(self, cur, prev=None, action=None, cost=0):
        # Mỗi nút có vị trí hiện tại (cur), nút trước đó (prev), và hành động từ nút trước
        self.cur = cur
        self.prev = prev
        self.action = action
        self.cost = cost

class MazeGame:
    def __init__(self, root, grid_size=20, cell_size=30,ratio=75):
        # Thiết lập các thông số ban đầu cho giao diện mê cung
        self.root = root
        self.ratio = ratio
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.start = None  # Điểm bắt đầu
        self.goal = None  # Điểm kết thúc
        # Khởi tạo lưới mê cung mặc định không có tường (True)
        self.grid = [[True for _ in range(grid_size)] for _ in range(grid_size)]
        # Khởi tạo canvas để vẽ mê cung
        self.canvas = tk.Canvas(root, width=cell_size * grid_size, height=cell_size * grid_size)
        self.canvas.pack()
        self.tendency = None

        # Gán sự kiện nhấp chuột để tạo tường, nút đặt điểm bắt đầu, kết thúc và chạy thuật toán
        self.canvas.bind("<Button-1>", self.toggle_wall)
        tk.Button(root, text="Set Start", command=self.set_start).pack()
        tk.Button(root, text="Set Goal", command=self.set_goal).pack()
        tk.Button(root, text="Random Maze", command=self.random_maze).pack()
        tk.Button(root, text="Run Algorithm", command=self.run_algorithm).pack()
        tk.Button(root, text="Exit", command=root.quit).pack()
        self.draw_grid()

    def draw_grid(self):
        # Vẽ lưới mê cung trên giao diện, với các ô trắng là đường đi và ô đen là tường
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                color = "white" if self.grid[i][j] else "black"
                if [i, j] == self.start:
                    color = "blue"  # Màu xanh cho điểm bắt đầu
                elif [i, j] == self.goal:
                    color = "green"  # Màu xanh lá cho điểm kết thúc
                # Vẽ từng ô trên canvas
                self.canvas.create_rectangle(j * self.cell_size, i * self.cell_size,
                                             (j + 1) * self.cell_size, (i + 1) * self.cell_size,
                                             fill=color, outline="grey")

    def toggle_wall(self, event):
        # Thêm/xóa tường khi nhấp chuột vào các ô trong mê cung
        row, col = event.y // self.cell_size, event.x // self.cell_size
        if [row, col] != self.start and [row, col] != self.goal:
            self.grid[row][col] = not self.grid[row][col]  # Đảo trạng thái ô
            self.draw_grid()

    def set_start(self):
        # Thiết lập điểm bắt đầu bằng cách nhấp chuột
        self.canvas.bind("<Button-1>", self._set_start)

    def _set_start(self, event):
        # Xác định và lưu vị trí điểm bắt đầu
        row, col = event.y // self.cell_size, event.x // self.cell_size
        self.start = [row, col]
        self.draw_grid()
        self.canvas.unbind("<Button-1>")

    def set_goal(self):
        # Thiết lập điểm kết thúc bằng cách nhấp chuột
        self.canvas.bind("<Button-1>", self._set_goal)

    def _set_goal(self, event):
        # Xác định và lưu vị trí điểm kết thúc
        row, col = event.y // self.cell_size, event.x // self.cell_size
        self.goal = [row, col]
        self.tendency = [self.goal[0] - self.start[0] , self.goal[1] - self.start[1]] 
        self.draw_grid()
        self.canvas.unbind("<Button-1>")

    def random_maze(self):
        # Tạo ngẫu nhiên mê cung bằng cách thêm/tạo các ô tường
        self.start = None
        self.goal = None
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                # Xác suất tạo đường đi cao hơn tường
                self.grid[i][j] = True if random.randint(0,100) < self.ratio else False
        self.draw_grid()

    def run_algorithm(self):
        # Chạy thuật toán tìm đường, yêu cầu điểm bắt đầu và kết thúc đã được đặt
        if not self.start or not self.goal:
            print("Chọn điểm bắt đầu và kết thúc trước!")
            return
        self.find_path()

    def find_path(self):
        # Hàm thực hiện thuật toán tìm đường từ điểm bắt đầu đến điểm kết thúc
        queue = PriorityQueue()
        start_node = Node(self.start)
        # Đưa nút bắt đầu vào hàng đợi ưu tiên với giá trị heuristic
        queue.put((self.heuristic(start_node),id(start_node), start_node))
        explored_set = set()

        while not queue.empty():
            _, _,  node = queue.get()
            explored_set.add(tuple(node.cur))
            new_position = [node.cur[0],node.cur[1]]
            if new_position != self.start:
                self.canvas.create_rectangle(new_position[1] * self.cell_size, new_position[0] * self.cell_size,
                                                 (new_position[1] + 1) * self.cell_size, (new_position[0] + 1) * self.cell_size,
                                                 fill="yellow", outline="grey")
                self.canvas.update()
                time.sleep(0.05)

        
            if node.cur == self.goal:
                # Hiển thị đường đi nếu tìm thấy
                self.show_path(node)
                return

            # Kiểm tra các bước đi từ nút hiện tại theo các hướng UP, DOWN, LEFT, RIGHT
            for step in [UP, RIGHT, DOWN, LEFT]:
                new_pos = [node.cur[0] + step[0], node.cur[1] + step[1]]
                # Kiểm tra xem bước đi có hợp lệ không
                if (0 <= new_pos[0] < self.grid_size and 0 <= new_pos[1] < self.grid_size
                        and self.grid[new_pos[0]][new_pos[1]] and tuple(new_pos) not in explored_set):
                    new_node = Node(new_pos, node, step, node.cost + 1)
                    # Đưa nút mới vào hàng đợi ưu tiên
                    queue.put((self.heuristic(new_node), id(new_node), new_node))
                    # Đánh dấu các ô đã đi qua với màu vàng
        print("Không tìm thấy đường đi!")
        self.show_no_path_message()

    def show_no_path_message(self):
        # Hiển thị thông báo khi không tìm thấy đường đi
        self.canvas.create_text(self.grid_size * self.cell_size // 2, self.grid_size * self.cell_size // 2,
                                text="Không tìm thấy đường đi!", fill="red", font=("Arial", 20, "bold"))

    def show_path(self, node):
        # Hiển thị đường đi từ điểm bắt đầu đến điểm kết thúc nếu tìm thấy
        path = []
        while node.prev is not None:
            path.append(node.cur)
            node = node.prev
        path.reverse()  # Đảo ngược để hiển thị từ điểm bắt đầu đến điểm kết thúc
        for row, col in path:
            self.canvas.create_rectangle(col * self.cell_size, row * self.cell_size,
                                         (col + 1) * self.cell_size, (row + 1) * self.cell_size,
                                         fill="orange", outline="grey")
            self.canvas.update()
            time.sleep(0.05)

    def heuristic(self, node):
        # Hàm heuristic tính chi phí theo khoảng cách Manhattan từ điểm hiện tại đến điểm kết thúc
        goal_cost = abs(node.cur[0] - self.goal[0]) + abs(node.cur[1] - self.goal[1])
        return goal_cost + node.cost

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Path Finding")
    app = MazeGame(root, grid_size=15, cell_size=40,ratio=75)
    root.mainloop()
