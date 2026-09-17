class Solution {
    public boolean isMatch(String s, String p) {
        int m= s.length();
        int n =p.length();
        Boolean[][] dp = new Boolean[m + 1][n + 1];
        return helper(m,n ,s,p,dp);

    }
    public boolean helper(int i, int j, String s, String p, Boolean[][] dp) {
        if(i==0 && j==0) return true;
        if(j==0) return false;
        if(i==0){
            while(j>0){
                if(p.charAt(j-1)!='*'){
                    return false;
                   
                }
                j--;
                
            }
            return true;
        }
        if (dp[i][j] != null) return dp[i][j];
        if(s.charAt(i-1)==p.charAt(j-1) || p.charAt(j-1)=='?') {
            return helper(i-1,j-1,s,p,dp);

        }
        else if (p.charAt(j-1)=='*'){
            return dp[i][j] = helper(i, j - 1, s, p, dp) || helper(i - 1, j, s, p, dp);
        }
        else{
            return dp[i][j] = false;
        }
    }
}