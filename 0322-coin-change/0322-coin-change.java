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
        int[] dp = new int[amount + 1];
        Arrays.fill(dp, amount + 1);
        dp[0] = 0;

        for (int coin : coins) {
            for (int i = coin; i <= amount; i++) {
                dp[i] = Math.min(dp[i], 1 + dp[i - coin]);
            }
        }
        return dp[amount] > amount ? -1 : dp[amount];
        
    }
}