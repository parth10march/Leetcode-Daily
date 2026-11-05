class Solution {
    int[][] memo;
    int m,n;
    public int calculateMinimumHP(int[][] dungeon) {
        m =dungeon.length;
        n=dungeon[0].length;
        memo = new int[m][n];
        return solve(0,0,dungeon);
    }
    public int solve(int i,int j,int[][]grid){
        if(i>=m || j>=n) return (int) 1e9;
        if(i==m-1 && j==n-1) return Math.max(1,1-grid[i][j]);
        if (memo[i][j] != 0) return memo[i][j];
        int r=solve(i,j+1,grid);
        int d=solve(i+1,j,grid);
        int need=Math.min(r,d);
        return memo[i][j] = Math.max(1, need - grid[i][j]);
    }
}