class Solution {
    public int coinChange(int[] coins, int amount) {
        // int arr[] = new int[amount + 1];
        // for(int i = 0; i <= amount; i++){
        //     arr[i] = amount + 1;
        // }
        // arr[0] = 0;

        // for(int coin : coins){
        //     for(int i = coin; i <= amount; i++){
        //         arr[i] = Math.min(arr[i], 1 + arr[i - coin]);
        //     }
        // }

        // if(arr[amount] > amount){
        //     return - 1;
        // }
        // else{
        //     return arr[amount];



        // int[] dp = new int[amount + 1];
        // Arrays.fill(dp, amount + 1);
        // dp[0] = 0;

        // for (int coin : coins) {
        //     for (int i = coin; i <= amount; i++) {
        //         dp[i] = Math.min(dp[i], 1 + dp[i - coin]);
        //     }
        // }
        // return dp[amount] > amount ? -1 : dp[amount];




        int n = coins.length;
        int[][] dp = new int[n + 1][amount + 1];
        for (int j = 1; j <= amount; j++) {
            dp[0][j] = amount + 1;
        }
        for (int i = 1; i <= n; i++) {
            int coin = coins[i - 1];
            for (int j = 1; j <= amount; j++) {
                if (j < coin) {
                    dp[i][j] = dp[i - 1][j];
                } else {
                    dp[i][j] = Math.min(dp[i - 1][j], 1 + dp[i][j - coin]);
                }
            }
        }

        return dp[n][amount] > amount ? -1 : dp[n][amount];
        
    }
}