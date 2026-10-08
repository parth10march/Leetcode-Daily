class Solution {
    public int maxSumAfterPartitioning(int[] arr, int k) {
        int[] dp = new int[arr.length];
        java.util.Arrays.fill(dp, -1);
        return solve(0, arr, k, dp);
    }
    public int solve(int i,int[]arr,int k, int[]dp){
        if (i >= arr.length) return 0;
        if (dp[i] != -1) return dp[i];

        int max_num = -1;
        int result = 0;

        for (int j = i; j < arr.length && j < i + k; j++) {
            max_num = Math.max(max_num, arr[j]);
            int len = j - i + 1;
            int cost = max_num * len + solve(j + 1, arr, k, dp);
            result = Math.max(result, cost);
        }

        return dp[i] = result;
    }
}