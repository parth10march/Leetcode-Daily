class Solution {
    private static final int[] DR = {-1, 1, 0, 0};
    private static final int[] DC = {0, 0, -1, 1};
    public int numIslands(char[][] grid) {
        int m = grid.length;
        int n = grid[0].length;
        int con = 0;
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                if (grid[i][j] == '1') {
                    con++;
                    bfs(grid,i,j,m,n);
                }
            }
        }
        return con;
    }
    private void bfs(char[][] grid,int row,int col,int rows,int cols) {
        Queue<int[]> q = new LinkedList<>();
        grid[row][col] = '0';
        q.offer(new int[]{row,col});
        while (!q.isEmpty()) {
            int[] curr=q.poll();
            int r=curr[0];
            int c=curr[1];
            for (int i=0;i<4;i++) {
                int nr= r + DR[i];
                int nc =c + DC[i];
                if (nr>= 0 && nr<rows && nc>= 0 && nc <  cols && grid[nr][nc] == '1') {
                    grid[nr][nc] = '0';
                    q.offer(new int[]{nr,nc});
                }
            }
        }
    }
}