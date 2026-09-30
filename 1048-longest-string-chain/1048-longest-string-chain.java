class Solution {
    public int longestStrChain(String[] words) {
        Arrays.sort(words,(a,b)->a.length()-b.length());
        int n=words.length;
        int maxLen=1;
        int []dp= new int[n];
        for(int i=0;i<n;i++){
            dp[i]=1;
            for(int j=0;j<i;j++){
                if(isPred(words[j],words[i])){
                    dp[i]=Math.max(dp[i],1+dp[j]);
                }
            }
            maxLen=Math.max(dp[i],maxLen);
        }
        return maxLen;
    }
    public boolean isPred(String a, String b){
        int m=a.length();
        int n=b.length();
        if((n-m)!=1){
            return false;
        }
        int i=0;
        int j=0;
        while(i<m && j<n){
            if(a.charAt(i)==b.charAt(j)){
                i++;
            }
            j++;
        }
        return i==m;
    }
}