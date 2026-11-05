class Solution {
    public int subarraysWithKDistinct(int[] nums, int k) {
        return atmost(nums, k) - atmost(nums, k - 1);
    }
    public int atmost(int[] nums, int k){
        int cnt = 0;
        int l = 0, r = 0;
        HashMap<Integer, Integer> map = new HashMap<>();
        for(r = 0; r < nums.length; r++){    
            map.put(nums[r], map.getOrDefault(nums[r], 0) + 1);
            while (map.size() > k) {
                map.put(nums[l], map.get(nums[l]) - 1);
                if (map.get(nums[l]) == 0) map.remove(nums[l]);
                l++;
            }
            cnt = cnt + r - l + 1;
        }
        return cnt;
    }
}