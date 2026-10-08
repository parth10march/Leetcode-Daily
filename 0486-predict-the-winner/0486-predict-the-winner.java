class Solution {
    public boolean predictTheWinner(int[] nums) {
        int n = nums.length;
        return solve(0, nums.length - 1, nums) >= 0;
    }
    public int solve(int i,int j,int[]nums){
        if(i==j) return nums[i];
        int result=0;
        int left=nums[i]-solve(i+1,j,nums);
        int right=nums[j]-solve(i,j-1,nums);
        result =Math.max(left , right);
        return result;

    }
}