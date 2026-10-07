import java.util.Arrays;

class Solution {
    public int minCut(String s) {
        int n = s.length();
        int[] dp = new int[n];
        Arrays.fill(dp, -1);
        return helper(0, s, dp) - 1;
    }

    public int helper(int start, String s, int[] dp) {
        if (start == s.length()) {
            return 0;
        }
        if (dp[start] != -1) {
            return dp[start];
        }

        int ans = Integer.MAX_VALUE;
        for (int end = start; end < s.length(); end++) {
            if (isPalindrome(s, start, end)) {
                ans = Math.min(ans, 1 + helper(end + 1, s, dp));
            }
        }
        return dp[start] = ans;
    }

    private boolean isPalindrome(String s, int left, int right) {
        while (left < right) {
            if (s.charAt(left++) != s.charAt(right--)) {
                return false;
            }
        }
        return true;
    }
}