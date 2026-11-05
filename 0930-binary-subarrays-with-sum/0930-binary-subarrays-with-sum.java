class Solution {
    public int numSubarraysWithSum(int[] nums, int goal) {
        int n=nums.length;
        int count=0;
        for(int r=0;r<n;r++){
            int sum=0;
            for(int j=r;j<n;j++){
                sum+=nums[j];
                
                
                if(sum==goal){
                    count++;
                }
            }
        }
        return count;
    }
}