class Solution {
    public int longestArithSeqLength(int[] nums) {
        int n = nums.length;
        int ans = 2;

        List<HashMap<Integer, Integer>> dp = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            dp.add(new HashMap<>());
        }
        for (int i = 0; i < n; i++) {

            for (int j = 0; j < i; j++) {
                int diff = nums[i] - nums[j];


                int length = dp.get(j).getOrDefault(diff, 1) + 1;
                dp.get(i).put(diff, length);

                ans = Math.max(ans, length);
            }
        }

        return ans;
    }
}