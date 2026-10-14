class Solution {
    int[][] dp;
    public int splitArray(int[] nums, int k) {
        int n = nums.length;
        dp = new int[n][k + 1];
        for (int[] row : dp) {
            Arrays.fill(row, -1);
        }
        return solve(0, k, nums);
    }
    public int solve(int i, int k, int[] nums) {
        int n = nums.length;
        if (k == 1) {
            int sum = 0;
            for (int t = i; t < n; t++) {
                sum += nums[t];
            }
            return sum;
        }
        if (dp[i][k] != -1) {
            return dp[i][k];
        }
        int currSum = 0;
        int result = Integer.MAX_VALUE;
        for (int j = i; j <= n - k; j++) {
            currSum += nums[j];
            int remainingSum = solve(j + 1, k - 1, nums);

            int largeSum = Math.max(currSum, remainingSum);

            result = Math.min(result, largeSum);
        }

        return dp[i][k] = result;
    }
}