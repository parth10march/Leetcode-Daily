class Solution {
    public int longestSubsequence(int[] arr, int difference) {
        HashMap<Integer, Integer> map = new HashMap<>();
        int ans = 0;

        for (int num : arr) {
            int previous = num - difference;
            int length = map.getOrDefault(previous, 0) + 1;

            map.put(num, length);
            ans = Math.max(ans, length);
        }
        return ans;
    }
}