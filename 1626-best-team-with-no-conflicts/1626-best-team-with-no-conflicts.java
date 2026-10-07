class Solution {
    public int bestTeamScore(int[] scores, int[] ages) {
        int n = scores.length;
        int[][] players = new int[n][2];
        for (int i = 0; i < n; i++) {
            players[i][0] = scores[i];
            players[i][1] = ages[i];
        }

        Arrays.sort(players, (a, b) -> {
            if (a[1] != b[1]) {
                return Integer.compare(a[1], b[1]);
            }
            return Integer.compare(a[0], b[0]);
        });

        int[] dp = new int[n];
        int maxTotalScore = 0;

        for (int i = 0; i < n; i++) {
            dp[i] = players[i][0];
            for (int j = 0; j < i; j++) {
                if (players[i][0] >= players[j][0]) {
                    dp[i] = Math.max(dp[i], dp[j] + players[i][0]);
                }
            }
            maxTotalScore = Math.max(maxTotalScore, dp[i]);
        }

        return maxTotalScore;
    }
}