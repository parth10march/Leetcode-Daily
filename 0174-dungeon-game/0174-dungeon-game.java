// class Solution {
//     int[][] memo;
//     int m,n;
//     public int calculateMinimumHP(int[][] dungeon) {
//         m =dungeon.length;
//         n=dungeon[0].length;
//         memo = new int[m][n];
//         return solve(0,0,dungeon);
//     }
//     public int solve(int i,int j,int[][]grid){
//         if(i>=m || j>=n) return (int) 1e9;
//         if(i==m-1 && j==n-1) return Math.max(1,1-grid[i][j]);
//         if (memo[i][j] != 0) return memo[i][j];
//         int r=solve(i,j+1,grid);
//         int d=solve(i+1,j,grid);
//         int need=Math.min(r,d);
//         return memo[i][j] = Math.max(1, need - grid[i][j]);
//     }
// }

class Solution {
    public int calculateMinimumHP(int[][] dungeon) {
        int m = dungeon.length;
    int n = dungeon[0].length;       
        int h = 1;
        while (!canReach(h, dungeon, m, n)) {
            h++;
        }
        return h;
    }
    private boolean canReach(int initialHP, int[][] dungeon, int m, int n) {
        int[][] maxHP = new int[m][n];
        for (int[] row : maxHP) java.util.Arrays.fill(row, -1);
        int startHP = initialHP + dungeon[0][0];
        if (startHP <= 0) return false;
        maxHP[0][0] = startHP;
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                if (maxHP[i][j] <= 0) continue;
                if (i + 1 < m) {
                    int next = maxHP[i][j] + dungeon[i + 1][j];
                    if (next > 0) {
                        maxHP[i + 1][j] = Math.max(maxHP[i + 1][j], next);
                    }
                }
                if (j + 1 < n) {
                    int next = maxHP[i][j] + dungeon[i][j + 1];
                    if (next > 0) {
                        maxHP[i][j + 1] = Math.max(maxHP[i][j + 1], next);
                    }
                }
            }
        }
        return maxHP[m - 1][n - 1] > 0;
    }
}