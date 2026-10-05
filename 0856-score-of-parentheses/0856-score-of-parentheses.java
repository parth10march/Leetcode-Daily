class Solution {
    public int scoreOfParentheses(String s) {
        int sc=0;
        int dep=0;
        for(int i=0;i<s.length();i++){
            if(s.charAt(i)=='('){
                ++dep;

            }else{
                --dep;
                if(s.charAt(i-1)=='('){
                    sc+= 1<< dep;

                }
            }
        }
        return sc;
    }
}