class Solution {
    public int palindromePartition(String s, int k) {
        int n = s.length();
       int[][] dp = new int[n][k + 1];
        for (int i = 0; i < n; i++) {
            Arrays.fill(dp[i], -1);
        }
        return solve(0, k, s, dp);
    }
    public int solve(int i, int k, String s, int[][] dp) {
        int n = s.length();
        if (k == 1) {
            return cost(i, n - 1, s);
        }
        if (dp[i][k] != -1) {
            return dp[i][k];
        }
        int result = Integer.MAX_VALUE;
        for (int j = i; j <= n - k; j++) {
            int currentCost = cost(i, j, s);
            int remainingCost = solve(j + 1, k - 1, s, dp);
            int totalCost = currentCost + remainingCost;
            result = Math.min(result, totalCost);
        }
        return dp[i][k] = result;
    }
    public int cost(int i, int j, String s) {
        int changes = 0;
        while (i < j) {
            if (s.charAt(i) != s.charAt(j)) {
                changes++;
            }
            i++;
            j--;
        }
        return changes;
    }
}