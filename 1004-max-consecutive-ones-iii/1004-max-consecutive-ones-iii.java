class Solution {
    public int longestOnes(int[] arr, int k) {
        int n=arr.length;
        int left=0;
        int right=0;
        int cz=0;
        int maxl=0;
        for(right=0;right<n;right++){
            if(arr[right]==0){
                cz++;
            }
            while(cz>k){
                if(arr[left]==0){
                    cz--;
                }
                left++;
                
            }
           maxl = Math.max(maxl, right - left + 1);
            
        }
        return maxl;
    }
}