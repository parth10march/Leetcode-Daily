class Solution {
    public int minCost(int[][] grid) {
        int m = grid.length;
        int n = grid[0].length;
        boolean[][] dp = new boolean[n][1024];
        for (int i = 0; i < m; i++) {
            boolean[][] next = new boolean[n][1024];
            for (int j = 0; j < n; j++) {
                int val = grid[i][j];
                if (i == 0 && j == 0) {
                    next[0][val] = true;
                    continue;
                }
                for (int x = 0; x < 1024; x++) {
                    if ((i > 0 && dp[j][x]) || (j > 0 && next[j - 1][x])) {
                        next[j][x ^ val] = true;
                    }
                }
            }
            dp = next;
        }
        for (int x = 0; x < 1024; x++) {
            if (dp[n - 1][x]) {
                return x;
            }
        }
        return -1;
    }
}