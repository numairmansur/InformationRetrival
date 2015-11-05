// Copyright 2015, University of Freiburg,
// Chair of Algorithms and Data Structures.
// Hannah Bast <bast@cs.uni-freiburg.de>.

import java.io.IOException;

public class ListIntersectionMain {
    public static void main(String[] args) throws IOException {
        String listNames[] = { "film", "comedy" };
//        String listNames[] = { "film", "2015" };
//        String listNames[] = { "2015", "comedy" };
        int m = listNames.length;
        ListIntersection li = new ListIntersection();

        // Read lists.
        PostingList lists[] = new PostingList[m];
        System.out.println();

        for (int i = 0; i < m; i++) {
            System.out.print("Reading list \"" + listNames[i] + "\" ... ");
            System.out.flush();
            String fileName = "postinglists/" + listNames[i] + ".txt";
//            lists[i] = li.readPostingList(fileName, 100, 200 * 1000);
            lists[i] = li.readPostingList(fileName, 1, 0);
            System.out.println("done, size = " +  lists[i].ids.length);
        }
        System.out.println();

        // Performance test.
        // for (int i = 0; i < m; i++) {
        // li.performanceTest(lists[i], listNames[i]); }

        long totalTime = 0;
        int numOfTests = 10;

        // Performance test for our intersect.
        for (int run = 0; run < numOfTests; run++) {
            System.out.print("Intersecting \"" + listNames[0] + "\" with \"" + listNames[0] + "\" ...");
            System.out.flush();
            long time1 = System.currentTimeMillis();

            // Linear Time Intersection
//            li.intersect(lists[0], lists[1]);

            // Binary Search Intersection
            if (lists[0].ids.length < lists[1].ids.length) {
                li.intersectBinarySearch(lists[0], lists[1]);
            } else {
                li.intersectBinarySearch(lists[1], lists[0]);
            }

            long time2 = System.currentTimeMillis();
            long delta = time2 - time1;
            System.out.println("done in " + delta + "ms");
            totalTime += delta;
        }
        System.out.print("\nIntersecting \"" + listNames[0] + "\" with \"" + listNames[1] + "\" ...");
        System.out.println("average time is " + (totalTime / numOfTests) + "ms");
    }
}
